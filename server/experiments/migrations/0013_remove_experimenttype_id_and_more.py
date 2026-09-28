# experiments/migrations/0013_remove_experimenttype_id_and_more.py

from django.db import migrations, models


# populated by capture_mappings, consumed by repair_m2m
_id_to_name = {}


def capture_mappings(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM experiments_librarypreptype")
        _id_to_name["library_prep_type"] = dict(cursor.fetchall())

        cursor.execute("SELECT id, name FROM experiments_experimenttype")
        _id_to_name["experiment_type"] = dict(cursor.fetchall())


def repair_m2m(apps, schema_editor):
    ExperimentRNAShortRead = apps.get_model("experiments", "ExperimentRNAShortRead")

    def repair(field_name, through_table, fk_column):
        field = ExperimentRNAShortRead._meta.get_field(field_name)
        id_to_name = _id_to_name[field_name]

        with schema_editor.connection.cursor() as cursor:
            cursor.execute(f"SELECT experimentrnashortread_id, {fk_column} FROM {through_table}")
            existing_links = cursor.fetchall()

        # rebuild the through table so its FK column matches the new
        # varchar PK, FK constraint, and indexes
        schema_editor.remove_field(ExperimentRNAShortRead, field)
        schema_editor.add_field(ExperimentRNAShortRead, field)

        through = field.remote_field.through
        to_create = [
            through(experimentrnashortread_id=exp_id, **{fk_column: id_to_name[old_id]})
            for exp_id, old_id in existing_links
        ]
        through.objects.bulk_create(to_create)

    repair("library_prep_type", "experiments_experimentrnashortread_library_prep_type", "librarypreptype_id")
    repair("experiment_type", "experiments_experimentrnashortread_experiment_type", "experimenttype_id")


def noop(apps, schema_editor):
    pass


def irreversible(apps, schema_editor):
    raise migrations.exceptions.IrreversibleError(
        "This migration repairs orphaned M2M data and cannot be reversed."
    )


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0012_fix_preptargetsdetail_m2m"),
    ]

    operations = [
        migrations.RunPython(capture_mappings, noop),
        migrations.RemoveField(
            model_name="experimenttype",
            name="id",
        ),
        migrations.RemoveField(
            model_name="historicalexperimenttype",
            name="id",
        ),
        migrations.RemoveField(
            model_name="historicallibrarypreptype",
            name="id",
        ),
        migrations.RemoveField(
            model_name="librarypreptype",
            name="id",
        ),
        migrations.AlterField(
            model_name="experimenttype",
            name="name",
            field=models.CharField(
                choices=[
                    ("single-end", "single-end"),
                    ("paired-end", "paired-end"),
                    ("targeted", "targeted"),
                    ("untargeted", "untargeted"),
                ],
                max_length=255,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="librarypreptype",
            name="name",
            field=models.CharField(
                choices=[
                    ("stranded poly-A pulldown", "stranded poly-A pulldown"),
                    ("stranded total RNA", "stranded total RNA"),
                    ("rRNA depletion", "rRNA depletion"),
                    ("globin depletion", "globin depletion"),
                    ("custom", "custom"),
                ],
                max_length=255,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.RunPython(repair_m2m, irreversible),
    ]