// src/utils/schemaAndTables.js

export const getValidationRules = (key, schema, requiredFields = []) => {
  const rules = [];

  if (requiredFields.includes(key)) {
    rules.push({ required: true, message: `${key} is required` });
  }

  if (schema.enum) {
    rules.push({
      validator: (_, value) => {
        const isRequired = requiredFields.includes(key);
        if (!isRequired && (value === undefined || value === null || value === "")) {
          return Promise.resolve();
        };
        return schema.enum.includes(value)
          ? Promise.resolve()
          : Promise.reject(new Error(`${key} must be one of: ${schema.enum.join(", ")}`));
      },
    });
  }

  if (schema.type === "string") {
    if (schema.minLength)
      rules.push({ min: schema.minLength, message: `${key} must be at least ${schema.minLength} characters` });
    if (schema.maxLength)
      rules.push({ max: schema.maxLength, message: `${key} must be at most ${schema.maxLength} characters` });
  }

  if (schema.type === "number" || schema.type === "integer") {
    if (schema.minimum !== undefined)
      rules.push({ type: "number", min: schema.minimum, message: `${key} must be at least ${schema.minimum}` });
    if (schema.maximum !== undefined)
      rules.push({ type: "number", max: schema.maximum, message: `${key} must be at most ${schema.maximum}` });
  }

  return rules;
};

export const foreignKeyFields = {
  participant: {
    family_id: {
      sourceTable: "families",
      valueKey: "family_id",
      apiKey: "family",
    },
    twin_id: {
      sourceTable: "participants",
      valueKey: "participant_id",
      apiKey: "participant",
    }
  },
  phenotype: {
    participant_id: {
      sourceTable: "participants",
      valueKey: "participant_id",
      apiKey: "participant",
    }
  },
  analyte: {
    participant_id: {
      sourceTable: "participants",
      valueKey: "participant_id",
      apiKey: "participant",
    }
  },
  genetic_findings: {
    experiment_id: {
      sourceTable: "experiments",
      valueKey: "experiment_id",
      apiKey: "experiment",
    },
    participant_id: {
      sourceTable: "participants",
      valueKey: "participant_id",
      apiKey: "participant",
    }
  },
  biobank: {
    participant_id: {
      sourceTable: "participants",
      valueKey: "participant_id",
      apiKey: "participant",
    },
    child_analytes:{
      sourceTable: "analytes",
      valueKey: "analyte_id",
      apiKey: "analyte",
    },
    experiments: {
      sourceTable: "experiments",
      valueKey: "experiment_id",
      apiKey: "experiment",
    },
    alignments: {
      sourceTable: "aligned",
      valueKey: "aligned_id",
      apiKey: "aligned",
    }
  },
  experiment_dna_short_read: {
    analyte_id:{
      sourceTable: "analytes",
      valueKey: "analyte_id",
      apiKey: "analyte",
    }
  },
  experiment_rna_short_read: {
    analyte_id:{
      sourceTable: "analytes",
      valueKey: "analyte_id",
      apiKey: "analyte",
    }
  },
  experiment_pac_bio: {
    analyte_id:{
      sourceTable: "analytes",
      valueKey: "analyte_id",
      apiKey: "analyte",
    }
  },
  experiment_nanopore: {
    analyte_id:{
      sourceTable: "analytes",
      valueKey: "analyte_id",
      apiKey: "analyte",
    }
  },
  aligned_dna_short_read: {
    experiment_dna_short_read_id:{
      sourceTable: "experiment_dna_short_read",
      valueKey: "experiment_dna_short_read_id",
      apiKey: "experiment_dna_short_read",
    }
  },
  aligned_rna_short_read: {
    experiment_rna_short_read_id:{
      sourceTable: "experiment_rna_short_read",
      valueKey: "experiment_rna_short_read_id",
      apiKey: "experiment_rna_short_read",
    }
  },
  aligned_pac_bio: {
    experiment_pac_bio_id:{
      sourceTable: "experiment_pac_bio",
      valueKey: "experiment_pac_bio_id",
      apiKey: "experiment_pac_bio",
    }
  },
  aligned_nanopore: {
    experiment_nanopore_id:{
      sourceTable: "experiment_nanopore",
      valueKey: "experiment_nanopore_id",
      apiKey: "experiment_nanopore",
    }
  },
};

export const defaultVisibleColumns = {
  participants: ["participant_id", "proband_relationship", "family_id", "solve_status"],
  genetic_findings: ["genetic_findings_id", "participant_id", "experiment_id"],
  analytes: ["analyte_id", "participant_id", "analyte_type"],
  families: ["family_id", "consanguinity", "family_history_detail"],
  biobank_entries: ["biobank_id", "participant", "child_analytes", "alignments", "experiments", "current_location", "status"],
  phenotypes: ["participant_id", "term_id", "ontology", "additional_details"],
  experiment_dna_short_read: ["experiment_dna_short_read_id", "analyte_id", "experiment_sample_id"],
  experiment_rna_short_read: ["experiment_rna_short_read_id","analyte_id", "experiment_sample_id"],
  experiment_pac_bio: ["experiment_pac_bio_id", "analyte_id", "experiment_sample_id"],
  experiment_nanopore: ["experiment_nanopore_id", "analyte_id", "experiment_sample_id"],
  aligned_dna_short_read: ["aligned_dna_short_read_id"],
  aligned_nanopore: ["aligned_nanopore_id"],
  aligned_pac_bio: ["aligned_pac_bio_id"],
  aligned_rna_short_read: ["aligned_rna_short_read_id"],
};

export const onsetAgeRange = {
  "unknown" : "Unknown",
  "HP:0003581" : "Adult onset",
  "HP:0030674" : "Antenatal onset",
  "HP:0011463" : "Childhood onset",
  "HP:0003577" : "Congenital onset",
  "HP:0025708" : "Early young adult onset",
  "HP:0011460" : "Embryonal onset",
  "HP:0011461" : "Fetal onset",
  "HP:0003593" : "Infantile onset",
  "HP:0025709" : "Intermediate young adult onset",
  "HP:0003621" : "Juvenile onset",
  "HP:0034199" : "Late first trimester onset",
  "HP:0003584" : "Late onset",
  "HP:0025710" : "Late young adult onset",
  "HP:0003596" : "Middle age onset",
  "HP:0003623" : "Neonatal onset",
  "HP:0410280" : "Pediatric onset",
  "HP:4000040" : "Puerpural onset",
  "HP:0034198" : "Second trimester onset",
  "HP:0034197" : "Third trimester onset",
  "HP:0011462" : "Young adult onset"
}

export const primaryBiosample = {
	"UBERON:0000479": "tissue",
	"UBERON:0003714": "neural tissue",
	"UBERON:0001836": "saliva",
	"UBERON:0001003": "skin epidermis",
	"UBERON:0002385": "muscle tissue",
	"UBERON:0000178": "whole blood",
	"UBERON:0002371": "bone marrow",
	"UBERON:0006956": "buccal mucosa",
	"UBERON:0001359": "cerebrospinal fluid",
	"UBERON:0001088": "urine",
	"UBERON:0019306": "nose epithelium",
	"CL: 0000034": "iPSC",
	"CL: 0000576": "monocytes - PBMCs",
	"CL: 0000542": "lymphocytes - LCLs",
	"CL: 0000057": "fibroblasts",
	"UBERON:0005291": "embryonic tissue",
	"CL: 0011020": "iPSC NPC",
	"UBERON:0002037": "cerebellum tissue",
	"UBERON:0001133": "cardiac tissue"
}

export const specimenType = {
  "D": "EDTA in Cryovial",
  "R": "PAX Tube",
  "OG": "OGR-500 saliva collection kit",
  "SC": "OCD-100 buccal collection kit",
  "SG": "OGR-675 buccal collection kit",
  "X": "Extracted DNA",
  "XR": "Extracted RNA"
}

export const TABLE_MAPPING = [
  { name: "Participants", schema: "participants", identifier: "participant_id" },
  { name: "Families", schema: "families", identifier: "family_id" },
  { name: "Genetic Findings", schema: "genetic_findings", identifier: "genetic_findings_id" },
  { name: "Analytes", schema: "analytes", identifier: "analyte_id" },
  { name: "Biobank Entries", schema: "biobank_entries", identifier: "biobank_id" },
  { name: "Phenotypes", schema: "phenotypes", identifier: "phenotype_id" },
  { name: "DNA Short Read", schema: "experiment_dna_short_read", identifier: "experiment_dna_short_read_id" },
  { name: "RNA Short Read", schema: "experiment_rna_short_read", identifier: "experiment_rna_short_read_id" },
  { name: "PacBio", schema: "experiment_pac_bio", identifier: "experiment_pac_bio_id" },
  { name: "NanoPore", schema: "experiment_nanopore", identifier: "experiment_nanopore_id" },
  { name: "Aligned DNA Short Read", schema: "aligned_dna_short_read", identifier: "aligned_dna_short_read_id" },
  { name: "Aligned NanoPore", schema: "aligned_nanopore", identifier: "aligned_nanopore_id" },
  { name: "Aligned Pac Bio", schema: "aligned_pac_bio", identifier: "aligned_pac_bio_id" },
  { name: "Aligned RNA Short Read", schema: "aligned_rna_short_read", identifier: "aligned_rna_short_read_id" },
];

/**
 * Get collection name from schema key
 * @param {string} schema - Schema name from TABLE_MAPPING
 * @returns {string|null} Identifier-friendly collection name
 */
export const getCollectionName = (schema) => {
  const entry = TABLE_MAPPING.find(item => item.schema === schema);
  return entry ? entry.identifier.replace(/_id$/, "") : null;
};

/**
 * Get schema key from collection name
 * @param {string} collectionName - Short collection name (no _id)
 * @returns {string|null} Schema key
 */
export const getTableName = (collectionName) => {
  const entry = TABLE_MAPPING.find(item => 
    item.identifier.replace(/_id$/, "") === collectionName
  );
  if (collectionName === "aligned") {
    return "aligned"
  }
  if (collectionName === "experiment") {
    return "experiments"
  }
  return entry ? entry.schema : null;
};

/**
 * Get primary key field for any schema
 * @param {string} Schema key
 * @returns {string|null} Primary key field
 */
export const getIdentifier = (schema) => {
  return TABLE_MAPPING.find(item => item.schema === schema)?.identifier || null;
};
