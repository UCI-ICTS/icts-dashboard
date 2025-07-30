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
      value_key: "family_id",
      apiKey: "family",
    },
    maternal_id: {
      sourceTable: "participants",
      value_key: "participant_id",
      apiKey: "participant",
    },
    paternal_id: {
      sourceTable: "participants",
      value_key: "participant_id",
      apiKey: "participant",
    },
    twin_id: {
      sourceTable: "participants",
      value_key: "participant_id",
      apiKey: "participant",
    }
  },
  phenotype: {
    participant_id: {
      sourceTable: "participants",
      value_key: "participant_id",
      apiKey: "participant",
    }
  },
  analyte: {
    participant_id: {
      sourceTable: "participants",
      value_key: "participant_id",
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
    experiment_dna_short_read_id:{
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

