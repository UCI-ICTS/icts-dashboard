#gregordb/metadata.py

"""
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

class Participant(models.Model):

    # https://stackoverflow.com/questions/63255065/storing-arrays-in-django-models-not-postgresql
    # class InternalProjectId(models.Model):
    #         project_id = models.CharField(max_length=255)
    #         participant_id = models.ForeignKey(
    #             Participant,
    #             related_name='project_id',
    #             on_delete=models.CASCADE
    #         )

    class GregorCenter(models.TextChoices):
        BCM = "BCM", _("Baylor College of Medicine Research Center")
        BROAD = "BROAD", _("Broad Institute")
        CNHI = "CNH_I", _("Children’s National Hospital")
        UWCRDR = "UW_CRDR", _("University of Washington Center for Rare Disease Research")
        GSS = "GSS", _("GREGoR Stanford Site")
        UWDCC = "UW_DCC", _("University of Washington’s School of Public Health")
    
    class ConsentCode(models.TextChoices):
        GRU = "GRU", _("GRU")
        HMB = "HMB", _("HMB")
    
    class Recontactable(models.TextChoices):
        YES = "yes", _("yes")
        NO = "no", _("no")

    participant_id = models.CharField(
        unique=True,
        primary_key=True,
        max_length=255,
        help_text="Subject/Participant Identifier (primary key)"
        )
    internal_project_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="An identifier used by GREGoR research centers to identify" \
        "a set of participants for their internal tracking"
        )
    gregor_center = models.CharField(
        max_length=255,
        blank=True,
        choices=GregorCenter.choices,
        default=None,
        help_text="GREGoR Center to which the participant is originally associated"
        )
    consent_code = models.CharField(
        max_length=255,
        choices=ConsentCode.choices,
        help_text="Consent group pertaining to this participant's data"
        )
    recontactable = models.CharField(
        max_length=255,
        blank=True,
        choices=Recontactable.choices,
        help_text="Is the originating GREGoR Center likely able to recontact this participant"
        )
    prior_testing = models.TextField(
        blank=True,
        help_text="Text description of any genetic testing for individual conducted prior to enrollment"
        )
    pmid_id = models.CharField(
        blank=True,
        max_length=255,
        help_text="Case specific PubMed ID if applicable"
        )
    family_id = models.CharField(
        max_length=255,
        help_text="Identifier for family"
        )
    paternal_id = models.CharField(
        max_length=255,
        help_text="participant_id for father; 0 if not available"
        )
    maternal_id = models.CharField(
        max_length=255,
        help_text="participant_id for mother; 0 if not available"
        )
    twin_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="participant_id for twins, triplets, etc; 0 if not available"
        )
    proband_relationship = models.CharField(
        max_length=255,
        help_text="Text description of individual relationship to proband in family, especially useful to capture relationships when connecting distant relatives and connecting relatives not studied"
        )
    proband_relationship_detail = models.TextField(
        blank=True,
        help_text="Other proband relationship not captured in enumeration above"
        )
    sex = models.CharField(
        max_length=255,
        help_text="Biological sex assigned at birth (aligned with All of Us). If individual has a known DSD / not expected sex chromosome karyotype, this can be noted in the phenotype information section."
        )
    sex_detail = models.TextField(
        blank=True,
        help_text="Optional free-text field to describe known discrepancies between 'sex' value (female=>XX, male=>XY) and actual sex chromosome karyotype"
        )
    reported_race = models.CharField(
        max_length=255,
        blank=True,
        help_text="Self/submitter-reported race (OMB categories"
        )
    reported_ethnicity = models.CharField(
        max_length=255,
        blank=True,
        help_text="Self/submitter-reported ethnicity (OMB categories)"
        )
    ancestry_detail = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional specific ancestry description free text beyond what is captured by OMB race/ethnicity categories"
        )
    age_at_last_observation = models.CharField(
        max_length=255,
        blank=True,
        help_text="Age at last observation, aka age in years at the last time the center can vouch for the accuracy phenotype data. For conditions with later age of onset, this field lets users know if individuals marked as unaffected were younger or older than the age when the phenotype is expected to appear"
        )
    affected_status = models.TextField(
        blank=True,
        help_text="Indicate affected status of individual (overall with respect to primary phenotype in the family). Note: Affected participants must have entry in phenotype table."
        )
    phenotype_description = models.TextField(
        blank=True,
        help_text="human-readable 'Phenotypic one-line summary' for why this individual is of interest. Could be the same as the term_details value in the Phenotype table. Strongly encourage/required for proband."
        )
    age_at_enrollment = models.CharField(
        max_length=255,
        blank=True,
        help_text="age in years at which consent was originally obtained"
        )
    solve_status = models.CharField(
        max_length=255,
        help_text="Indication of whether the submitting RC considers this case 'solved'"
        )
    missing_variant_case = models.TextField(
        blank=True,
        help_text="Indication of whether this is known to be a missing variant case, see notes for a description of the Missing Variant Project and inclusion criteria."
    )
    missing_variant_details = models.TextField(
        blank=True,
        help_text="For missing variant cases, indicate gene(s) or region of interest and reason for inclusion in MVP"
    )
    #example values for fields
    participant_id.help_text += ' Example values: BCM_Subject_1, BROAD_subj89054.'

    def __str__(self):
        return str(self.participant_id)