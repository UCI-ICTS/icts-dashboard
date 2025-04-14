#!/usr/bin/env python
# metadata/models.py

"""
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from submodels.models import (
    ReportedRace,
    InternalProjectId,
    PmidId,
    VariantType,
    VariantInheritance,
    Zygosity,
    GeneDiseaseValidity,
    DiscoveryMethod,
    GregorCenter,
    ConsentCode,
    YesNo,
    Consanguinity,
    TwinId,
    ProbandRelationship,
    BiologicalSex,
    ReportedEthnicity
)


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


class Participant(models.Model):
    participant_id = models.CharField(
        unique=True,
        primary_key=True,
        max_length=255,
        help_text="Subject/Participant Identifier (primary key)",
    )
    internal_project_id = models.ManyToManyField(
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
    prior_testing = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="Text description of any genetic testing for individual "
        "conducted prior to enrollment",
    )
    pmid_id = models.ManyToManyField(
        PmidId,
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
    twin_id = models.ManyToManyField(
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
    reported_race = models.ManyToManyField(
        ReportedRace,
        related_name="participants",
        blank=True,
        help_text="Self/submitter-reported race (OMB categories)",
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
    phenotype_description = models.JSONField(
        default=list,
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

    def get_pmid_id(self):
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
    additional_modifiers = models.JSONField(
        default=list, blank=True, help_text="List of additional modifiers (HPO/MONDO terms)"
    )
    syndromic = models.CharField(
        max_length=50,
        choices=[("syndromic", "syndromic"), ("non-syndromic", "non-syndromic")],
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
    experiment_id = models.JSONField(
        default=list,
        help_text="The experiment table and experiment ID(s) in which discovery was identified",
    )
    variant_type = models.JSONField(
        default=list,
        choices=VariantType.choices,
        help_text="Type of genetic variant"
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
    gene_of_interest = models.JSONField(
        default=list,
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
    condition_inheritance = models.JSONField(
        default=list,
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
    method_of_discovery = models.JSONField(
        default=list,
        blank=True,
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
        default="No",
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

    internal_analyte_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="UCI identifier for an analyte from a primary biosample source",
    )

    def __str__(self):
        return f"Analyte {self.analyte_id} from participant {self.participant_id.participant_id}"


class Biobank(models.Model):
    biobank_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for a biosample in repository",
    )
    participant_id = models.ForeignKey(
        Participant,
        to_field="participant_id",
        db_column="participant_id",
        on_delete=models.CASCADE,
        help_text="The participant from whom the biosample was taken",
    )
    collection_date = models.DateField(
        help_text="Date when the biosample was created"
    )
    specimen_type = models.CharField(
        max_length=10,
        choices=[
            ("D", "EDTA in Cryovial"),
            ("R", "PAX Tube"),
            ("SC", "OCD-100 buccal collection kit"),
            ("SG", "OGR-675 saliva collection kit"),
            ("X", "Extracted DNA"),
            ("XR","Extracted RNA")
        ],
        help_text="Analyte codes printed on biospecimen containers"
    )
    current_location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Sample storage location, e.g. UCI, Ambry, CNH"
    )
    freezer_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Name of freezer or refrigerator the biospecimen is stored in"
    )
    shelf_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Name of freezer/refrigerator shelf the biospecimen is stored in"
    )
    rack_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Name of rack the biospecimen is stored in"
    )
    box_type = models.CharField(
        max_length=50,
        choices=[
            ("5x5 cryobox", "5x5 cryobox"),
            ("9x9 cryobox", "9x9 cryobox"),
            ("10x10 cryobox", "10x10 cryobox"),
            ("SBS plate", "SBS plate"),
            ("Wire rack", "Wire rack"),
            ("8x12 metal rack", "8x12 metal rack")
        ],
        blank=True,
        null=True,
        help_text="Box type the biospecimen is stored in"
    )
    box_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Box name as labelled"
    )
    box_position = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="XY coordinates of biospecimens in box or plate, e.g. A01, H12"
    )
    tube_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Barcode on tube if present"
    )
    plate_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Barcode on SBS plate if present or used"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("Pending shipment", "Pending shipment"),
            ("Shipped", "Shipped"),
            ("Received", "Received"),
            ("Stored", "Stored"),
            ("Replacement requested", "Replacement requested, see comments"),
            ("Lost", "Lost, see comments"),
            ("QC issue", "QC issue, see comments")
        ],
        help_text="Biospecimen status while "
    )
    shipment_date = models.DateField(
        blank=True,
        null=True,
        help_text="If the status is shipped, then include a date when it was mailed out."
    )
    child_analytes = models.ManyToManyField(
        Analyte,
        related_name="analytes",
        blank=True,
        help_text="The analyte(s) derived from this biospecimen",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Free text description of any quality issues with biospecimens or adverse events."
    )
