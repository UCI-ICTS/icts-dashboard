// src/utils/schemaAndTables.js

/**
 * Parse values like:
 *  "CONDITIONAL (gene_known_for_phenotype = Known)"
 *  "CONDITIONAL (variant_type = SNV, variant_type = INDEL, variant_type = RE)"
 *  "CONDITIONAL (library_prep_type = custom)"
 *
 * Returns { op: 'ANY', tests: [{field, value}, ...] }
 *   - 'ANY' means any one test may satisfy (OR across comma-separated items)
 */
export const parseRequiredCondition = (raw) => {
  if (!raw || typeof raw !== "string") return null;
  const m = raw.match(/^CONDITIONAL\s*\((.*)\)\s*$/i);
  if (!m) return null;

  // Split on commas not inside quotes (simple tokens in our schemas)
  const parts = m[1].split(",").map(s => s.trim()).filter(Boolean);

  const tests = parts.map(p => {
    const eq = p.indexOf("=");
    if (eq === -1) return null;
    const field = p.slice(0, eq).trim();
    const value = p.slice(eq + 1).trim();
    return {
      field,
      value: value.replace(/^['"]|['"]$/g, "")
    };
  }).filter(Boolean);

  return { op: "ANY", tests };
};

/**
 * Determine if the condition is satisfied given current form values.
 * Supports:
 *  - string or number fields with equality
 *  - array fields (condition satisfied if array includes the value)
 */
export const conditionSatisfied = (cond, getValue) => {
  if (!cond || !cond.tests?.length) return false;
  return cond.tests.some(({ field, value }) => {
    const v = getValue(field);
    if (Array.isArray(v)) return v.includes(value);
    return v === value;
  });
};

/**
 * Which form fields should trigger revalidation for this conditional?
 */
export const getConditionDependencies = (cond) =>
  cond?.tests?.map(t => t.field) ?? [];

/**
 * Build AntD rules for a field, including conditional required (x-required-condition),
 * enum checks, string length, and numeric ranges.
 */
export const getValidationRules = (key, schema, requiredFields = [], getValue = () => undefined) => {
  const rules = [];

  // Hard required from JSON Schema "required"
  if (requiredFields.includes(key)) {
    rules.push({ required: true, message: `${key} is required` });
  }

  // Conditional required via x-required-condition
  if (schema["x-required-condition"]) {
    const cond = parseRequiredCondition(schema["x-required-condition"]);
    if (cond) {
      rules.push({
        validator: async (_, value) => {
          const mustHaveValue = conditionSatisfied(cond, (name) => getValue(name));
          if (!mustHaveValue) return Promise.resolve();

          const empty =
            value === undefined ||
            value === null ||
            (typeof value === "string" && value.trim() === "") ||
            (Array.isArray(value) && value.length === 0);
          if (empty) {
            throw new Error(
              `${key} is required when ${cond.tests.map(t => `${t.field} = ${t.value}`).join(" OR ")}`
            );
          }
          return Promise.resolve();
        },
        // INTERNAL marker for SchemaField to attach dependencies to Form.Item
        _conditionalDependencies: getConditionDependencies(cond),
      });
    }
  }

  // Enum check (supports string or array of enums)
  if (schema.enum) {
    rules.push({
      validator: (_, value) => {
        const isRequired = requiredFields.includes(key);
        const isEmpty =
          value === undefined ||
          value === null ||
          (typeof value === "string" && value === "");
        if (!isRequired && isEmpty) return Promise.resolve();

        return schema.enum.includes(value)
          ? Promise.resolve()
          : Promise.reject(new Error(`${key} must be one of: ${schema.enum.join(", ")}`));
      },
    });
  } else if (schema.type === "array" && schema.items?.enum) {
    rules.push({
      validator: (_, value) => {
        if (value == null) return Promise.resolve(); // handled by required rule if needed
        if (!Array.isArray(value)) {
          // Try to coerce string to array
          if (typeof value === 'string') {
            const trimmed = value.trim();
            if (trimmed === '') return Promise.resolve();
            value = trimmed.split('|').map(s => s.trim());
          } else {
            return Promise.reject(new Error(`${key} must be a list`));
          }
        }

        const bad = value.filter(v => !schema.items.enum.includes(v));
        return bad.length
          ? Promise.reject(new Error(`${key} contains invalid value(s): ${bad.join(", ")}. Allowed: ${schema.items.enum.join(", ")}`))
          : Promise.resolve();
      },
    });
  }

  // String length
  if (schema.type === "string") {
    if (schema.minLength)
      rules.push({ min: schema.minLength, message: `${key} must be at least ${schema.minLength} characters` });
    if (schema.maxLength)
      rules.push({ max: schema.maxLength, message: `${key} must be at most ${schema.maxLength} characters` });
  }

  // Numeric range
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
      default: "0"                         // add a default of `0`
    },
    paternal_id: {
      sourceTable: "participants",
      valueKey: "participant_id",
      apiKey: "participant",
      default: "0"                        // add a default of `0`
    },
    maternal_id: {
      sourceTable: "participants",
      valueKey: "participant_id",
      apiKey: "participant",
      default: "0"                         // add a default of `0`
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
    },
    partial_contribution_explained: {
      sourceTable: "phenotypes",
      valueKey: "term_id",
      apiKey: "phenotype",
      filterBy: "participant_id",          // tells SchemaForm what to filter on
      dependsOn: "participant_id"          // tells SchemaForm to watch this field
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

export const specimenType = {  // Biobank specific mappings
  "D": "EDTA in Cryovial",
  "R": "PAX Tube",
  "OG": "OGR-500 saliva collection kit",
  "SC": "OCD-100 buccal collection kit",
  "SG": "OGR-675 buccal collection kit",
  "X": "Extracted DNA",
  "XR": "Extracted RNA"
}

export const collectionSource = [
  { value: "Clinical Lab CNH", label: "Clinical Lab CNH" },
  { value: "CRU", label: "CRU" },
  { value: "Inpatient", label: "Inpatient" },
  { value: "Mailed Buccal", label: "Mailed Buccal" },
  { value: "mobile phlebotomy", label: "mobile phlebotomy" },
  { value: "Offsite", label: "Offsite" },
  { value: "other", label: "other" },
  { value: "Outpatient", label: "Outpatient" },
  { value: "UCI CCR", label: "UCI CCR" },
]

export const currentLocation = [
  { value: "Ambry", label: "Ambry Genetics" },
  { value: "CNH", label: "Children's National Hospital" },
  { value: "Invitae", label: "Invitae" },
  { value: "PacBio", label: "PacBio" },
  { value: "Seqmatic", label: "Seqmatic" },
  { value: "UCI", label: "UCI Vilain Lab" },
  { value: "UCSC", label: "UCSC" },
]

export const freezerId = [
  { value: "Banana", label: "Banana Fridge: +4C (next to lab door)" },
  { value: "Pom Pom Purin", label: "Pom Pom Purin: +4C (next to office)" },
  { value: "Dalgona", label: "Dalgona: -20C (right-most -20C)" },
  { value: "Bruno Mars", label: "Bruno Mars: -20C" },
  { value: "Appa", label: "Appa: -20C" },
  { value: "Eevee", label: "Eevee: -20C (left-most -20C)" },
  { value: "Hatsune Miku", label: "Hatsune Miku: -80C (right-side -80C)" },
  { value: "Lebron James", label: "Lebron James: -80C (left-side -80C)" },
  { value: "Boris Yeltsin", label: "Boris Yeltsin: LN2 dewer (next to office)" },
]

export const shelfId = [
  { value: "1", label: "1: Top shelf" },
  { value: "2", label: "2: Middle shelf" },
  { value: "3", label: "3: Middle lower shelf" },
  { value: "4", label: "4: Bottom shelf" },
]

export const rackId = [
  { value: "PMGRC-Frozen-Blood", label: "PMGRC Frozen Blood" },
  { value: "PAX RNA Rack 1", label: "PAX RNA Rack 1" },
  { value: "PAX RNA Rack 2", label: "PAX RNA Rack 2" },
  { value: "Saliva rack 1", label: "Saliva rack 1" },
  { value: "Saliva rack 2", label: "Saliva rack 2" },
  { value: "Saliva rack 3", label: "Saliva rack 3" },
]

export const testIndication = [
  { value: "Research", label: "Research" },
]

export const requestedTest = [
  { value: "10500", label: "10500" },
  { value: "10525", label: "10525" },
  { value: "Invitae WGS", label: "Invitae WGS" },
  { value: "CNH WGS", label: "CNH WGS" },
  { value: "Seqmatic RNA-seq", label: "Seqmatic RNA-seq" },
]

export const internalAnalysis = [
  { value: "wgs-calling v.0.7.0", label: "SR-GS snakemake" },
  { value: "leafcutter pipeline", label: "SR-RNAseq leafcutter pipeline" },
  { value: "PacBio-HiFi-human-WGS-WDL-v1.0", label: "PacBio WGS WDL v1.0" },
  { value: "PacBio-HiFi-human-WGS-WDL-v2.0", label: "PacBio WGS WDL v2.0" },
  { value: "UCSC Nanopore pipeline", label: "UCSC Nanopore pipeline" },
]

export const biobankMapping = {
  "collection_source": collectionSource,
  "current_location": currentLocation,
  "freezer_id": freezerId,
  "shelf_id": shelfId,
  "rack_id": rackId,
  "test_indication": testIndication,
  "requested_test": requestedTest,
  "internal_analysis": internalAnalysis,
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
