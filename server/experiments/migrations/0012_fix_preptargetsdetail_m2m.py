# experiments/migrations/0012_fix_preptargetsdetail_m2m.py

from django.db import migrations


# old bigint PrepTargetsDetail.id -> new PrepTargetsDetail.name
# fill these in from your mapping
ID_TO_NAME = {
    1: "Illumina Ribo-Zero Plus rRNA Depletion Kit",
    2: "NEBNext rRNA Depletion Kit v2 (Human/Mouse/Rat)",
    3: "NEBNext rRNA & Globin mRNA Depletion Kit (Human/Mouse/Rat)",
    4: "Watchmaker Polaris Depletion",
    5: "KAPA RiboErase (HMR) Globin",
}


def forwards(apps, schema_editor):
    ExperimentRNAShortRead = apps.get_model("experiments", "ExperimentRNAShortRead")
    field = ExperimentRNAShortRead._meta.get_field("prep_targets_detail")

    # 1. capture existing links before the mistyped through table is dropped
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT experimentrnashortread_id, preptargetsdetail_id "
            "FROM experiments_experimentrnashortread_prep_targets_detail"
        )
        existing_links = cursor.fetchall()

    # 2. drop the mistyped (orphaned FK, bigint) through table and recreate
    #    it — now correctly typed varchar, since PrepTargetsDetail's pk
    #    is a CharField as of 0011
    schema_editor.remove_field(ExperimentRNAShortRead, field)
    schema_editor.add_field(ExperimentRNAShortRead, field)

    # 3. re-insert the links, translating old bigint ids to their name values
    through = field.remote_field.through
    to_create = []
    for exp_id, old_id in existing_links:
        name = ID_TO_NAME.get(old_id)
        if name is None:
            raise RuntimeError(f"No mapping entry for old PrepTargetsDetail id {old_id!r}")
        to_create.append(through(experimentrnashortread_id=exp_id, preptargetsdetail_id=name))
    through.objects.bulk_create(to_create)


def backwards(apps, schema_editor):
    raise migrations.exceptions.IrreversibleError(
        "This migration repairs orphaned M2M data and cannot be reversed."
    )


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0011_remove_historicalpreptargetsdetail_id_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]