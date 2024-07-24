#!/usr/bin/env python
# metadata/models.py

"""
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class InternalProjectId(models.Model):
    internal_project_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="An identifier used by GREGoR research centers to identify "
        "a set of participants for their internal tracking",
    )

    def __str__(self):
        return self.internal_project_id


class VariantType(models.TextChoices):
    SNVINDEL = "SNV/INDEL", "Single Nucleotide Variant or Insertion/Deletion"
    SV = "SV", "Structural Variant"
    RE = "RE", "Repeat Expansion"


class Zygosity(models.TextChoices):
    HOMOZYGOUS = "Homozygous", "Homozygous"
    HETEROZYGOUS = "Heterozygous", "Heterozygous"
    HEMIZYGOUS = "Hemizygous", "Hemizygous"
    HETEROPLASMY = "Heteroplasmy", "Heteroplasmy"
    HOMOPLASMY = "Homoplasmy", "Homoplasmy"
    MOSAIC = "Mosaic", "Mosaic"
    UNKNOWN = "Unknown", "Unknown"


class VariantInheritance(models.TextChoices):
    DE_NOVO = "de novo", "De Novo"
    MATERNAL = "maternal", "Maternal"
    PATERNAL = "paternal", "Paternal"
    BIPARENTAL = "biparental", "Biparental"
    NONMATERNAL = "nonmaternal", "Nonmaternal"
    NONPATERNAL = "nonpaternal", "Nonpaternal"
    UNKNOWN = "unknown", "Unknown"


class GeneDiseaseValidity(models.TextChoices):
    VALID = "Valid", "Valid"
    INVALID = "Invalid", "Invalid"


class DiscoveryMethod(models.TextChoices):
    SR_ES = "SR-ES", "Short Read Exome Sequencing"
    SR_GS = "SR-GS", "Short Read Genome Sequencing"
    LR_GS = "LR-GS", "Long Read Genome Sequencing"
    SNP_ARRAY = "SNP array", "SNP Array"
    OPTICAL_MAPPING = "Optical mapping", "Optical Mapping"
    KARYOTYPE = "Karyotype", "Karyotype"
    SR_RNA_SEQ = "SR RNA-seq", "Short Read RNA Sequencing"
    LR_RNA_SEQ = "LR RNA-seq", "Long Read RNA Sequencing"
    SR_ES_REANALYSIS = "SR-ES-reanalysis", "Short Read Exome Sequencing Reanalysis"
    SR_GS_REANALYSIS = "SR-GS-reanalysis", "Short Read Genome Sequencing Reanalysis"
    LR_GS_REANALYSIS = "LR-GS-reanalysis", "Long Read Genome Sequencing Reanalysis"
    SNP_ARRAY_REANALYSIS = "SNP array-reanalysis", "SNP Array Reanalysis"
    OPTICAL_MAPPING_REANALYSIS = (
        "Optical mapping-reanalysis",
        "Optical Mapping Reanalysis",
    )
    KARYOTYPE_REANALYSIS = "Karyotype-reanalysis", "Karyotype Reanalysis"
    SR_RNA_SEQ_REANALYSIS = (
        "SR RNA-seq-reanalysis",
        "Short Read RNA Sequencing Reanalysis",
    )
    LR_RNA_SEQ_REANALYSIS = (
        "LR RNA-seq-reanalysis",
        "Long Read RNA Sequencing Reanalysis",
    )


class GregorCenter(models.TextChoices):
    BCM = "BCM", _("Baylor College of Medicine Research Center")
    BROAD = "BROAD", _("Broad Institute")
    CNH_I = "CNH_I", _("Children's National Hospital")
    UCI = "UCI", _("University of California Irvine")
    UW_CRDR = "UW_CRDR", _("University of Washington Center for Rare Disease Research")
    GSS = "GSS", _("GREGoR Stanford Site")
    UW_DCC = "UW_DCC", _("University of Washington’s School of Public Health")


class ConsentCode(models.TextChoices):
    GRU = "GRU", _("GRU")
    HMB = "HMB", _("HMB")


class YesNo(models.TextChoices):
    YES = "Yes", _("Yes")
    NO = "No", _("No")


class Consanguinity(models.TextChoices):
    NONE_SUSPECTED = "None suspected", _("None suspected")
    SUSPECTED = "Suspected", _("Suspected")
    PRESENT = "Present", _("Present")
    UNKNOWN = "Unknown", _("Unknown")


class PmidId(models.Model):
    pmid_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Publication which included participant; Used for "
        "publications which include participant known prior to or after"
        " inclusion in GREGoR",
    )

    def __str__(self):
        return str(self.pmid_id)


class Family(models.Model):
    family_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for family (primary key). Needs to be Unique across centers, use participant.gregor_center as ID prefix.",
    )
    consanguinity = models.CharField(
        max_length=50,
        choices=Consanguinity.choices,
        default=Consanguinity.UNKNOWN,
        help_text="Indicate if consanguinity is present or suspected within a family",
    )
    consanguinity_detail = models.TextField(
        blank=True,
        help_text="Free text description of any additional consanguinity details",
    )
    pedigree_file = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of file (renamed from pedigree_image because it can contain a PED file or image)",
    )
    pedigree_file_detail = models.TextField(
        blank=True,
        help_text="Free text description of other family structure/pedigree file caption or legend.",
    )
    family_history_detail = models.TextField(
        blank=True,
        help_text="Details about family history that do not fit into structured fields. Family relationship terms should be relative to the proband.",
    )


class TwinId(models.Model):
    twin_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="may be monozygotic, dizygotic, or polyzygotic",
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
    ASIAN = "Asian", _("ASIAN")
    BLACK = "Black or African American", _("BLACK")
    PACIFIC_ISLANDER = "Native Hawaiian or Other Pacific Islander", _(
        "PACIFIC_ISLANDER"
    )
    MIDDLE_EASTERN = "Middle Eastern or North African", _("MIDDLE_EASTERN")
    WHITE = "White", _("WHITE")


class ReportedEthnicity(models.TextChoices):
    HISPANIC = "Hispanic or Latino", _(
        "HISPANIC",
    )
    NON_HISPANIC = "Not Hispanic or Latino", _("NON_HISPANIC")


class PhenotypeDescription(models.Model):
    phenotype_description = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="For unaffected/relatives, can note 'parent of ...' or 'relative of ...'",
    )


class Participant(models.Model):
    participant_id = models.CharField(
        unique=True,
        primary_key=True,
        max_length=255,
        help_text="Subject/Participant Identifier (primary key)",
    )
    internal_project_ids = models.ManyToManyField(
        InternalProjectId,
        related_name="participants",
        blank=True,
        help_text="An identifier used by GREGoR research centers to identify"
        "a set of participants for their internal tracking",
    )
    gregor_center = models.CharField(
        max_length=255,
        blank=True,
        choices=GregorCenter.choices,
        default=None,
        help_text="GREGoR Center to which the participant is originally " "associated",
    )
    consent_code = models.CharField(
        max_length=255,
        choices=ConsentCode.choices,
        help_text="Consent group pertaining to this participant's data",
    )
    recontactable = models.CharField(
        max_length=255,
        blank=True,
        choices=YesNo.choices,
        default="No",
        help_text="Is the originating GREGoR Center likely able to recontact "
        "this participant",
    )
    prior_testing = models.TextField(
        blank=True,
        help_text="Text description of any genetic testing for individual "
        "conducted prior to enrollment",
    )
    pmid_ids = models.ManyToManyField(
        "PmidId",
        related_name="participants",
        blank=True,
        help_text="Case specific PubMed ID if applicable",
    )
    family_id = models.ForeignKey(
        Family,
        to_field="family_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Identifier for family",
    )
    paternal_id = models.CharField(
        max_length=255,
        default="0",
        help_text="participant_id for father; 0 if not available",
    )
    maternal_id = models.CharField(
        max_length=255,
        default="0",
        help_text="participant_id for mother; 0 if not available",
    )
    twin_ids = models.ManyToManyField(
        TwinId,
        related_name="participants",
        blank=True,
        help_text="participant_id for twins, triplets, etc; 0 if not available",
    )
    proband_relationship = models.CharField(
        max_length=255,
        choices=ProbandRelationship.choices,
        default=ProbandRelationship.UNKNOWN,
        help_text="Text description of individual relationship to proband in family, especially useful to capture relationships when connecting distant relatives and connecting relatives not studied",
    )
    proband_relationship_detail = models.TextField(
        blank=True,
        help_text="Other proband relationship not captured in enumeration above",
    )
    sex = models.CharField(
        max_length=255,
        choices=BiologicalSex.choices,
        default=BiologicalSex.UNKNOWN,
        help_text="Biological sex assigned at birth (aligned with All of Us). If individual has a known DSD / not expected sex chromosome karyotype, this can be noted in the phenotype information section.",
    )
    sex_detail = models.TextField(
        blank=True,
        help_text="Optional free-text field to describe known discrepancies between 'sex' value (female=>XX, male=>XY) and actual sex chromosome karyotype",
    )
    reported_race = models.CharField(
        max_length=255,
        blank=True,
        help_text="Self/submitter-reported race (OMB categories",
    )
    reported_ethnicity = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        choices=ReportedEthnicity.choices,
        help_text="Self/submitter-reported ethnicity (OMB categories)",
    )
    ancestry_detail = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional specific ancestry description free text beyond what is captured by OMB race/ethnicity categories",
    )
    age_at_last_observation = models.FloatField(
        null=True,
        blank=True,
        help_text="Age at last observation, aka age in years at the last time the center can vouch for the accuracy phenotype data. For conditions with later age of onset, this field lets users know if individuals marked as unaffected were younger or older than the age when the phenotype is expected to appear",
    )
    affected_status = models.TextField(
        blank=True,
        help_text="Indicate affected status of individual (overall with respect to primary phenotype in the family). Note: Affected participants must have entry in phenotype table.",
    )
    phenotype_description = models.TextField(
        blank=True,
        help_text="human-readable 'Phenotypic one-line summary' for why this individual is of interest. Could be the same as the term_details value in the Phenotype table. Strongly encourage/required for proband.",
    )
    age_at_enrollment = models.FloatField(
        null=True,
        blank=True,
        help_text="age in years at which consent was originally obtained",
    )
    solve_status = models.CharField(
        max_length=255,
        help_text="Indication of whether the submitting RC considers this case 'solved'",
    )
    missing_variant_case = models.TextField(
        blank=True,
        help_text="Indication of whether this is known to be a missing variant case, see notes for a description of the Missing Variant Project and inclusion criteria.",
    )
    missing_variant_details = models.TextField(
        blank=True,
        help_text="For missing variant cases, indicate gene(s) or region of interest and reason for inclusion in MVP",
    )

    def __str__(self):
        return str(self.participant_id)

    def get_pmid_ids(self):
        """Returns a list of primary key IDs for associated PmidIds."""
        return list(self.pmid_id.values_list("id", flat=True))


class Phenotype(models.Model):
    phenotype_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Unique identifier for the phenotype entry. This ID generated when loading into AnVIL data table and is not included in the uploaded .tsv file",
    )
    participant_id = models.ForeignKey(
        Participant,
        to_field="participant_id",
        db_column="participant_id",
        on_delete=models.CASCADE,
        related_name="phenotypes",
        help_text="Identifier for the participant associated with this phenotype.",
    )
    term_id = models.CharField(
        max_length=255, help_text="Identifier for the term within the ontology"
    )
    presence = models.CharField(
        max_length=100,
        choices=[("Present", "Present"), ("Absent", "Absent"), ("Unknown", "Unknown")],
        default="unknown",
        help_text="Indicates if the phenotype is present, absent, or unknown.",
    )
    ontology = models.CharField(
        max_length=100,
        choices=[
            ("HPO", "Human Phenotype Ontology"),
            ("MONDO", "Mondo Disease Ontology"),
            ("OMIM", "Online Mendelian Inheritance in Man"),
            ("ORPHANET", "Orphanet"),
            ("SNOMED", "Systematized Nomenclature of Medicine"),
            ("ICD10", "International Classification of Diseases - 10"),
        ],
        default="hpo",
        help_text="The ontology used to classify the phenotype term",
    )
    additional_details = models.TextField(
        blank=True,
        help_text="modifier of a term where the additional details are not supported/available as a term in HPO",
    )
    onset_age_range = models.CharField(
        max_length=100,
        choices=[
            ("HP:0003581", "Neonatal"),
            ("HP:0030674", "Infantile"),
            ("HP:0011463", "Childhood"),
            ("HP:0003577", "Adolescence"),
            ("HP:0025708", "Adult"),
            ("HP:0011460", "Old Age"),
            ("HP:0011461", "Young Adult"),
            ("HP:0003593", "Middle Age"),
            ("HP:0025709", "Late Adult"),
            ("HP:0003621", "All"),
            ("HP:0034199", "Early Childhood"),
            ("HP:0003584", "Late Childhood"),
            ("HP:0025710", "Young Middle Age"),
            ("HP:0003596", "Late Neonatal"),
            ("HP:0003623", "Late"),
            ("HP:0410280", "Early Neonatal"),
            ("HP:4000040", "Late Infancy"),
            ("HP:0034198", "Second Decade"),
            ("HP:0034197", "Third Decade"),
            ("HP:0011462", "First Decade"),
        ],
        default="unknown",
        help_text="Age range at the onset of the phenotype",
    )
    additional_modifiers = models.TextField(
        blank=True, help_text="Additional modifiers that further specify the phenotype"
    )
    syndromic = models.CharField(
        max_length=50,
        choices=[["syndromic", "non-syndromic"]],
        default="non-syndromic",
        help_text="Indicates if the phenotype is part of a syndromic condition",
    )

    def __str__(self):
        return f"{self.participant_id.participant_id} - {self.term_id}"


class GeneticFindings(models.Model):
    genetic_findings_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Unique ID of this variant in this participant",
    )
    participant_id = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        help_text="Subject/Participant Identifier within project",
    )
    experiment_id = models.CharField(
        max_length=255,
        help_text="The experiment table and experiment ID(s) in which discovery was identified",
    )
    variant_type = models.CharField(
        max_length=50, choices=VariantType.choices, help_text="Type of genetic variant"
    )
    sv_type = models.CharField(
        max_length=50, blank=True, help_text="Type of structural variant if applicable"
    )
    variant_reference_assembly = models.CharField(
        max_length=50, help_text="The genome build for identifying the variant position"
    )
    chrom = models.CharField(max_length=10, help_text="Chromosome of the variant")
    chrom_end = models.CharField(
        max_length=10, blank=True, help_text="End position chromosome of SV"
    )
    pos = models.IntegerField(help_text="Start position of the variant")
    pos_end = models.IntegerField(blank=True, null=True, help_text="End position of SV")
    ref = models.CharField(max_length=255, help_text="Reference allele of the variant")
    alt = models.CharField(max_length=255, help_text="Alternate allele of the variant")
    copy_number = models.IntegerField(
        blank=True, null=True, help_text="CNV copy number"
    )
    ClinGen_allele_ID = models.CharField(
        max_length=255,
        blank=True,
        help_text="ClinGen Allele ID for cross table reference",
    )
    gene_of_interest = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="HGNC approved symbol of the known or candidate gene(s)",
    )
    transcript = models.CharField(
        max_length=255,
        blank=True,
        help_text="Text description of transcript overlapping the variant",
    )
    hgvsc = models.CharField(
        max_length=255, blank=True, help_text="HGVS c. description of the variant"
    )
    hgvsp = models.CharField(
        max_length=255, blank=True, help_text="HGVS p. description of the variant"
    )
    hgvs = models.CharField(
        max_length=255, blank=True, help_text="Genomic HGVS description of the variant"
    )
    zygosity = models.CharField(
        max_length=50, choices=Zygosity.choices, help_text="Zygosity of variant"
    )
    allele_balance_or_heteroplasmy_percentage = models.FloatField(
        blank=True,
        null=True,
        help_text="Reported allele balance (mosaic) or heteroplasmy percentage (mitochondrial)",
    )
    variant_inheritance = models.CharField(
        max_length=50,
        choices=VariantInheritance.choices,
        help_text="Detection of variant in parents",
    )
    linked_variant = models.CharField(
        max_length=255, blank=True, help_text="Second variant in recessive cases"
    )
    linked_variant_phase = models.CharField(
        max_length=50, blank=True, help_text="Phase of linked variants"
    )
    gene_known_for_phenotype = models.CharField(
        max_length=50,
        blank=True,
        help_text="Indicate if the gene listed is a candidate or known disease gene",
    )
    known_condition_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Condition name consistent with the variant/phenotype/inheritance",
    )
    condition_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="MONDO/OMIM number for condition used for variant interpretation",
    )
    condition_inheritance = models.CharField(
        max_length=50,
        blank=True,
        help_text="Expected inheritance of the condition used for variant interpretation",
    )
    GREGoR_variant_classification = models.CharField(
        max_length=50,
        blank=True,
        help_text="Clinical significance of variant described to condition listed as determined by the RC's variant curation",
    )
    GREGoR_ClinVar_SCV = models.CharField(
        max_length=255,
        blank=True,
        help_text="ClinVar accession number for the variant curation submitted by your center",
    )
    gene_disease_validity = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=GeneDiseaseValidity.choices,
        help_text="Validity assessment of the gene-disease relationship",
    )
    public_database_other = models.CharField(
        max_length=255,
        blank=True,
        help_text="Public databases that this variant in this participant has been submitted by the RC",
    )
    public_database_ID_other = models.CharField(
        max_length=255, blank=True, help_text="Public database variant/case ID"
    )
    phenotype_contribution = models.CharField(
        max_length=50,
        blank=True,
        help_text="Contribution of variant-linked condition to participant's phenotype",
    )
    partial_contribution_explained = models.JSONField(
        blank=True,
        default=list,
        help_text="Specific phenotypes explained by the condition associated with this variant/gene in cases of partial contribution",
    )
    additional_family_members_with_variant = models.ManyToManyField(
        Participant,
        blank=True,
        related_name="family_variants",
        help_text="List of related participant IDs carrying the same variant",
    )
    method_of_discovery = models.CharField(
        max_length=50,
        blank=True,
        choices=DiscoveryMethod.choices,
        help_text="The method/assay(s) used to identify the candidate",
    )
    notes = models.TextField(
        blank=True,
        help_text="Free text field to explain edge cases or discovery updates or list parallel experiment IDs or list parental allele balance when mosaic... etc.",
    )

    def __str__(self):
        return self.genetic_findings_id


class Analyte(models.Model):
    analyte_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for an analyte from a primary biosample source",
    )
    participant_id = models.ForeignKey(
        Participant,
        to_field="participant_id",
        db_column="participant_id",
        on_delete=models.CASCADE,
        related_name="analytes",
        help_text="The participant from whom the biosample was taken",
    )
    analyte_type = models.CharField(
        max_length=50,
        choices=[
            ("DNA", "DNA"),
            ("RNA", "RNA"),
            ("cDNA", "cDNA"),
            ("blood plasma", "blood plasma"),
            ("frozen whole blood", "frozen whole blood"),
            ("high molecular weight DNA", "high molecular weight DNA"),
            ("urine", "urine"),
        ],
        help_text="Analyte derived from the primary biosample. The actual thing you're sticking into a machine to analyze/sequence",
    )
    analyte_processing_details = models.TextField(
        null=True,
        blank=True,
        help_text="Details about how the analyte or original biosample was extracted or processed",
    )
    primary_biosample = models.CharField(
        max_length=100,
        choices=[
            ("UBERON:0000479", "tissue"),
            ("UBERON:0003714", "neural tissue"),
            ("UBERON:0001836", "saliva"),
            ("UBERON:0001003", "skin epidermis"),
            ("UBERON:0002385", "muscle tissue"),
            ("UBERON:0000178", "whole blood"),
            ("UBERON:0002371", "bone marrow"),
            ("UBERON:0006956", "buccal mucosa"),
            ("UBERON:0001359", "cerebrospinal fluid"),
            ("UBERON:0001088", "urine"),
            ("UBERON:0019306", "nose epithelium"),
            ("CL:0000034", "iPSC"),
            ("CL:0000576", "monocytes - PBMCs"),
            ("CL:0000542", "lymphocytes - LCLs"),
            ("CL:0000057", "fibroblasts"),
            ("UBERON:0005291", "embryonic tissue"),
            ("CL:0011020", "iPSC NPC"),
            ("UBERON:0002037", "cerebellum tissue"),
            ("UBERON:0001133", "cardiac tissue"),
        ],
        help_text="Tissue type of biosample taken from the participant that the analyte was extracted or processed from",
    )
    primary_biosample_id = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="Optional ID for the biosample; allows for linking of multiple analytes extracted or processed from the same biosample",
    )
    primary_biosample_details = models.TextField(
        blank=True,
        null=True,
        help_text="Free text to capture information not in structured fields",
    )
    tissue_affected_status = models.CharField(
        max_length=50,
        choices=YesNo.choices,
        default=False,
        help_text="If applicable to disease (suspected mosaic), indicates if the tissue is from an affected source.",
    )
    age_at_collection = models.FloatField(
        blank=True,
        null=True,
        help_text="Age of participant in years at biosample collection",
    )
    participant_drugs_intake = models.TextField(
        blank=True,
        null=True,
        help_text="The list of drugs patient is on, at the time of sample collection. Helpful during analysis of metabolomics and immune assays",
    )
    participant_special_diet = models.TextField(
        blank=True,
        null=True,
        help_text="If the patient was fasting, when the sample was collected. Relevant when analyzing metabolomics data",
    )
    hours_since_last_meal = models.FloatField(
        null=True,
        blank=True,
        help_text="Hours since last meal, relevant when analyzing metabolomics data",
    )
    passage_number = models.IntegerField(
        blank=True,
        null=True,
        help_text="Passage number is relevant for fibroblast cultures and possibly iPSC.",
    )
    time_to_freeze = models.FloatField(
        blank=True,
        null=True,
        help_text="Time (in hours) from collection to freezing the sample. Delayed freeze turns out to be useful / important info for PaxGene blood (for RNA isolation).",
    )
    sample_transformation_detail = models.TextField(
        blank=True, null=True, help_text="Details regarding sample transformation"
    )
    quality_issues = models.TextField(
        blank=True,
        null=True,
        help_text="Freetext (limited characters) to concisely describe if there are any QC issues that would be important to note",
    )

    def __str__(self):
        return f"Analyte {self.analyte_id} from participant {self.participant_id.participant_id}"
