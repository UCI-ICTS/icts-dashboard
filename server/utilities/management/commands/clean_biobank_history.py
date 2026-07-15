# metadata/management/commands/clean_biobank_history.py

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from metadata.models import Biobank


IGNORED_FIELDS = {
    # django-simple-history metadata
    "history_id",
    "history_date",
    "history_type",
    "history_change_reason",
    "history_user_id",

    # TimeStampedModel bookkeeping fields
    "created_at",
    "updated_at",
    "changed_by_id",
}


class Command(BaseCommand):
    """
    Remove consecutive HistoricalBiobank update rows that contain no
    meaningful Biobank-field changes.

    Creation (+) and deletion (-) records are always preserved. Update (~)
    rows are deleted only when their domain-field state is identical to the
    previously retained historical state for the same Biobank object.
    """

    help = (
        "Find and optionally delete HistoricalBiobank update records with "
        "no domain-field changes. Runs as a dry run unless --execute is used."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Actually delete matching historical records.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=5000,
            help="Number of history rows deleted per transaction. Default: 5000.",
        )
        parser.add_argument(
            "--username",
            help=(
                "Optionally restrict deletions to history created by one user, "
                "for example idedios."
            ),
        )

    def handle(self, *args, **options):
        execute = options["execute"]
        batch_size = options["batch_size"]
        username = options["username"]

        if batch_size < 1:
            raise CommandError("--batch-size must be at least 1.")

        history_model = Biobank.history.model
        original_pk = Biobank._meta.pk.attname

        comparison_fields = [
            field.attname
            for field in history_model._meta.concrete_fields
            if field.attname not in IGNORED_FIELDS
        ]

        query_fields = list(
            dict.fromkeys(
                [
                    original_pk,
                    "history_id",
                    "history_type",
                    "history_user_id",
                    *comparison_fields,
                ]
            )
        )

        queryset = (
            history_model.objects
            .order_by(
                original_pk,
                "history_date",
                "history_id",
            )
            .values(*query_fields)
            .iterator(chunk_size=batch_size)
        )

        previous_retained_state = {}
        delete_ids = []
        candidates = 0
        deleted = 0
        affected_objects = set()

        for row in queryset:
            object_id = row[original_pk]
            history_type = row["history_type"]

            current_state = tuple(
                row[field_name]
                for field_name in comparison_fields
            )

            previous_state = previous_retained_state.get(object_id)

            user_matches = True
            if username:
                # Resolve the username only for candidate rows later through
                # the query used for deletion. Here we retain the ID.
                user_matches = row["history_user_id"] is not None

            is_no_domain_change = (
                history_type == "~"
                and previous_state is not None
                and current_state == previous_state
            )

            if is_no_domain_change and user_matches:
                history_id = row["history_id"]

                if username:
                    belongs_to_user = history_model.objects.filter(
                        history_id=history_id,
                        history_user__username=username,
                    ).exists()

                    if not belongs_to_user:
                        # This row remains part of the retained sequence.
                        previous_retained_state[object_id] = current_state
                        continue

                candidates += 1
                affected_objects.add(object_id)

                if execute:
                    delete_ids.append(history_id)

                    if len(delete_ids) >= batch_size:
                        deleted += self.delete_batch(
                            history_model,
                            delete_ids,
                        )
                        delete_ids = []

                # Do not update previous_retained_state. The duplicate is
                # compared against the last retained meaningful state.
                continue

            # Always retain creations, deletions, and meaningful updates.
            previous_retained_state[object_id] = current_state

        if execute and delete_ids:
            deleted += self.delete_batch(history_model, delete_ids)

        self.stdout.write("")
        self.stdout.write(f"Candidate rows:   {candidates:,}")
        self.stdout.write(f"Affected objects: {len(affected_objects):,}")

        if username:
            self.stdout.write(f"Restricted user:  {username}")

        if execute:
            self.stdout.write(
                self.style.SUCCESS(f"Deleted rows:     {deleted:,}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Dry run only. No rows were deleted. "
                    "Use --execute after reviewing the result."
                )
            )

    @staticmethod
    def delete_batch(history_model, history_ids):
        """
        Delete one batch in its own transaction to avoid one enormous
        long-running transaction.
        """
        with transaction.atomic():
            deleted_count, _ = history_model.objects.filter(
                history_id__in=history_ids
            ).delete()

        return deleted_count