from django.db import migrations
class Migration(migrations.Migration):
    dependencies = [("hpo", "0003_hpoterm_hpo_term_tsv_gin_hpoterm_hpo_term_trgm_label_and_more")]
    operations = [
        migrations.RunSQL("UPDATE hpo_hpoterm SET search_tsv = to_tsvector('english',coalesce(label,'') || ' ' ||coalesce(synonyms_concat,'') || ' ' ||coalesce(definition,''));")
    ]
