from django.contrib.auth import get_user_model
from anvil.models import AnvilUpload
from anvil.services import validate_upload_source_data, generate_upload_tsvs, generate_upload_manifest, package_validation_run


user = get_user_model().objects.get(username="wheel")

upload = AnvilUpload.objects.create(
    upload_id="UCI_GREGoR_manifest_shell_test",
    changed_by=user,
)

from anvil.services import validate_upload_source_data



generate_upload_tsvs(
    upload=upload,
    output_dir="/tmp/anvil_uploads",
    changed_by=user,
)

manifest_result = generate_upload_manifest(
    upload=upload,
    output_dir="/tmp/anvil_uploads",
    changed_by=user,
)

manifest_result["manifest_path"]
manifest_result["manifest"]["summary"]

upload.refresh_from_db()
upload.status
upload.validation_runs.count()
upload.artifacts.count()
upload.upload_tables.count()

package_validation_run = validate_upload_package(
    upload=upload,
    changed_by=user,
)

package_validation_run.status
package_validation_run.error_count
package_validation_run.summary

for run in upload.validation_runs.order_by("started_at"):
    print(
        run.validator_version,
        run.status,
        run.error_count,
        run.started_at,
        run.finished_at,
    )
