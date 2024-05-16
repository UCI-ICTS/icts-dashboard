#us
#gregordb/metadata.py

"""
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

class InternalProjectId(models.Model):
    internal_project_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="An identifier used by GREGoR research centers to identify "\
            "a set of participants for their internal tracking"
    )

    def __str__(self):
        return self.internal_project_id

class GregorCenter(models.TextChoices):
    BCM = "BCM", _("Baylor College of Medicine Research Center")
    BROAD = "BROAD", _("Broad Institute")
    CNHI = "CNH_I", _("Children's National Hospital")
    UWCRDR = "UW_CRDR", _("University of Washington Center for Rare Disease Research")
    GSS = "GSS", _("GREGoR Stanford Site")
    UWDCC = "UW_DCC", _("University of Washington’s School of Public Health")

class ConsentCode(models.TextChoices):
    GRU = "GRU", _("GRU")
    HMB = "HMB", _("HMB")

class Recontactable(models.TextChoices):
    YES = "Yes", _("Yes")
    NO = "No", _("No")

class PmidId(models.Model):
    pmid_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Publication which included participant; Used for "\
            "publications which include participant known prior to or after"\
            " inclusion in GREGoR"
    )

class Family(models.Model):
    family_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text=""
    )

class TwinId(models.Model):
    twin_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="may be monozygotic, dizygotic, or polyzygotic"
    )
    def __str__(self):
        return self.twin_id

class ProbandRelationship(models.TextChoices):
    SELF = "Self", _("SELF")
    MOTHER = "Mother", _("MOTHER")
    FATHER = "Father", _("FATHER")
    SIBLING = "Sibling", _("SIBLING")
    CHILD = "Child", _("CHILD")
    MATERNAL_HALF_SIBLING = "Maternal Half Sibling", _("MATERNAL_HALF_SIBLING")
    PATERNAL_HALF_SIBLING = "Paternal Half Sibling", _("PATERNAL_HALF_SIBLING")
    MATERNAL_GRANDMOTHER = "Maternal Grandmother", _("MATERNAL_GRANDMOTHER")
    MATERNAL_GRANDFATHER = "Maternal Grandfather", _("MATERNAL_GRANDFATHER")
    PATERNAL_GRANDMOTHER = "Paternal Grandmother", _("PATERNAL_GRANDMOTHER")
    PATERNAL_GRANDFATHER = "Paternal Grandfather", _("PATERNAL_GRANDFATHER")
    MATERNAL_AUNT = "Maternal Aunt", _("MATERNAL_AUNT")
    MATERNAL_UNCLE = "Maternal Uncle", _("MATERNAL_UNCLE")
    PATERNAL_AUNT = "Paternal Aunt", _("PATERNAL_AUNT")
    PATERNAL_UNCLE = "Paternal Uncle", _("PATERNAL_UNCLE")
    NIECE = "Niece", _("NIECE")
    NEPHEW = "Nephew", _("NEPHEW")
    MATERNAL_FIRST_COUSIN = "Maternal 1st Cousin", _("MATERNAL_FIRST_COUSIN")
    PATERNAL_FIRST_COUSIN = "Paternal 1st Cousin", _("PATERNAL_FIRST_COUSIN")
    OTHER = "Other", _("OTHER")
    UNKNOWN = "Unknown", _("UNKNOWN")

class BiologicalSex(models.TextChoices):
    FEMALE = "Female", _("FEMALE")
    MALE = "Male", _("MALE")
    UNKNOWN = "Unknown", _("UNKNOWN")

class ReportedRace(models.TextChoices):
    NATIVE_AMERICAN = "American Indian or Alaska Native", _("NATIVE_AMERICAN")
    ASIAN = "Asian",_("ASIAN")
    BLACK = "Black or African American", _("BLACK")
    PACIFIC_ISLANDER = "Native Hawaiian or Other Pacific Islander", _("PACIFIC_ISLANDER")
    MIDDLE_EASTERN = "Middle Eastern or North African", _("MIDDLE_EASTERN")
    WHITE = "White", _("WHITE")

class ReportedEthnicity(models.TextChoices):
    HISPANIC = "Hispanic or Latino", _("HISPANIC",)
    NON_HISPANIC = "Not Hispanic or Latino", _("NON_HISPANIC")

class PhenotypeDescription(models.Model):
    phenotype_description = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="For unaffected/relatives, can note 'parent of ...' or 'relative of ...'"
    )
    
class Participant(models.Model):
    participant_id = models.CharField(
        unique=True,
        primary_key=True,
        max_length=255,
        help_text="Subject/Participant Identifier (primary key)"
        )
    internal_project_id = models.ManyToManyField(
        InternalProjectId,
        related_name="participant",
        blank=True,
        help_text="An identifier used by GREGoR research centers to identify" \
        "a set of participants for their internal tracking"
        )
    gregor_center = models.CharField(
        max_length=255,
        blank=True,
        choices=GregorCenter.choices,
        default=None,
        help_text="GREGoR Center to which the participant is originally "\
            "associated"
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
        default="No",
        help_text="Is the originating GREGoR Center likely able to recontact "\
            "this participant"
        )
    prior_testing = models.TextField(
        blank=True,
        help_text="Text description of any genetic testing for individual "\
            "conducted prior to enrollment"
    )
    pmid_id = models.ManyToManyField(
        PmidId,
        related_name="participant",
        blank=True,
        help_text="Case specific PubMed ID if applicable"
    )
    family_id = models.OneToOneField(
        Family,
        null=True,
        blank=True,
        on_delete = models.SET_NULL,
        help_text="Identifier for family"
        )
    paternal_id = models.CharField(
        max_length=255,
        default="0",
        help_text="participant_id for father; 0 if not available"
        )
    maternal_id = models.CharField(
        max_length=255,
        default="0",
        help_text="participant_id for mother; 0 if not available"
        )
    twin_id = models.ManyToManyField(
        TwinId,
        related_name="participant",
        blank=True,
        help_text="participant_id for twins, triplets, etc; 0 if not available"
        )
    proband_relationship = models.CharField(
        max_length=255,
        choices=ProbandRelationship.choices,
        default=ProbandRelationship.UNKNOWN,
        help_text="Text description of individual relationship to proband in family, especially useful to capture relationships when connecting distant relatives and connecting relatives not studied"
        )
    proband_relationship_detail = models.TextField(
        blank=True,
        help_text="Other proband relationship not captured in enumeration above"
        )
    sex = models.CharField(
        max_length=255,
        choices=BiologicalSex.choices,
        default=BiologicalSex.UNKNOWN,
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
        default=None,
        choices=ReportedEthnicity.choices,
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
    
    def get_prior_testing_list(self):
        """Return a list of prior testing from the comma-separated string."""
        return self.prior_testing.split('|') if self.prior_testing else []

    def set_prior_testing_list(self, list_of_tests):
        """Set the prior_testing field from a list."""
        self.prior_testing = '|'.join(list_of_tests)
    
