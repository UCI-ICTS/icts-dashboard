#!/usr/bin/env python3
# utilities/management/commands/audit_history.py

from collections import defaultdict

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Count, Max, Min


HISTORY_METADATA_FIELDS = {
    "history_id",
    "history_date",
    "history_type",
    "history_change_reason",
    "history_user_id",

    # Ignore model audit fields when deciding whether the domain data changed
    "created_at",
    "updated_at",
    "changed_by_id",
}


class Command(BaseCommand):
    help = (
        "Audit django-simple-history records across tracked models. "
        "Reports live/history counts, date ranges, users, history types, "
        "and optionally consecutive duplicate historical states."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            dest="app_label",
            help="Restrict the audit to one Django app, for example metadata.",
        )
        parser.add_argument(
            "--model",
            dest="model_name",
            help="Restrict the audit to one model, for example Biobank.",
        )
        parser.add_argument(
            "--duplicates",
            action="store_true",
            help=(
                "Scan each historical table for consecutive records with "
                "identical tracked field values. This may take time."
            ),
        )
        parser.add_argument(
            "--top-users",
            type=int,
            default=10,
            help="Number of user/type groups to display. Default: 10.",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=2000,
            help="Iterator chunk size used during duplicate scanning.",
        )

    def handle(self, *args, **options):
        app_label = options["app_label"]
        model_name = options["model_name"]
        scan_duplicates = options["duplicates"]
        top_users = options["top_users"]
        chunk_size = options["chunk_size"]

        tracked_models = []

        for model in apps.get_models():
            if app_label and model._meta.app_label != app_label:
                continue

            if model_name and model.__name__.lower() != model_name.lower():
                continue

            history_manager = getattr(model, "history", None)
            if history_manager is None:
                continue

            tracked_models.append(model)

        if not tracked_models:
            self.stdout.write(
                self.style.WARNING("No history-enabled models matched.")
            )
            return

        for model in sorted(
            tracked_models,
            key=lambda item: item._meta.label_lower,
        ):
            self.audit_model(
                model=model,
                scan_duplicates=scan_duplicates,
                top_users=top_users,
                chunk_size=chunk_size,
            )

    def audit_model(
        self,
        model,
        scan_duplicates,
        top_users,
        chunk_size,
    ):
        history_model = model.history.model
        history_queryset = history_model.objects.all()

        live_count = model._base_manager.count()
        history_count = history_queryset.count()

        aggregate = history_queryset.aggregate(
            first_history=Min("history_date"),
            last_history=Max("history_date"),
        )

        ratio = history_count / live_count if live_count else 0

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(model._meta.label)
        )
        self.stdout.write(f"  Live records:       {live_count:,}")
        self.stdout.write(f"  Historical records: {history_count:,}")
        self.stdout.write(f"  History/live ratio: {ratio:,.2f}")
        self.stdout.write(
            f"  First history:      {aggregate['first_history']}"
        )
        self.stdout.write(
            f"  Last history:       {aggregate['last_history']}"
        )

        grouped = (
            history_queryset
            .values(
                "history_user__username",
                "history_type",
            )
            .annotate(count=Count("history_id"))
            .order_by("-count")[:top_users]
        )

        self.stdout.write("  Top history user/type groups:")

        if not grouped:
            self.stdout.write("    None")
        else:
            for row in grouped:
                username = row["history_user__username"] or "<none>"
                history_type = row["history_type"]
                count = row["count"]

                self.stdout.write(
                    f"    {username:24} "
                    f"{history_type:2} "
                    f"{count:>12,}"
                )

        if scan_duplicates:
            duplicate_results = self.count_consecutive_duplicates(
                model=model,
                history_model=history_model,
                chunk_size=chunk_size,
            )

            duplicate_count = duplicate_results["duplicates"]
            affected_objects = duplicate_results["affected_objects"]
            duplicate_ratio = (
                duplicate_count / history_count
                if history_count
                else 0
            )

            self.stdout.write(
                f"  Consecutive records with no domain-field changes: "
                f"{duplicate_count:,} "
                f"({duplicate_ratio:.1%})"
            )
            self.stdout.write(
                f"  Objects affected:       "
                f"{affected_objects:,}"
            )

    def count_consecutive_duplicates(
        self,
        model,
        history_model,
        chunk_size,
    ):
        """
        Count consecutive historical rows whose tracked model state is
        identical to the immediately preceding row for the same object.

        History metadata such as history_date, history_type, and history_user
        is deliberately excluded from the comparison.
        """
        original_pk_attname = model._meta.pk.attname

        comparison_fields = [
            field.attname
            for field in history_model._meta.concrete_fields
            if field.attname not in HISTORY_METADATA_FIELDS
        ]

        if original_pk_attname not in comparison_fields:
            comparison_fields.insert(0, original_pk_attname)

        query_fields = list(
            dict.fromkeys(
                comparison_fields
                + [
                    "history_id",
                    "history_date",
                ]
            )
        )

        queryset = (
            history_model.objects
            .order_by(
                original_pk_attname,
                "history_date",
                "history_id",
            )
            .values(*query_fields)
            .iterator(chunk_size=chunk_size)
        )

        previous_state_by_object = {}
        duplicate_counts_by_object = defaultdict(int)

        for row in queryset:
            object_id = row[original_pk_attname]

            current_state = tuple(
                row[field_name]
                for field_name in comparison_fields
            )

            previous_state = previous_state_by_object.get(object_id)

            if previous_state == current_state:
                duplicate_counts_by_object[object_id] += 1

            previous_state_by_object[object_id] = current_state

        return {
            "duplicates": sum(duplicate_counts_by_object.values()),
            "affected_objects": len(duplicate_counts_by_object),
        }