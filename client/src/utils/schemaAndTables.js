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
  genetic_findings: {
    experiment_id: {
      sourceTable: "experiments",
      valueKey: "experiment_id",
      apiKey: "experiment",  // or whatever makes sense
    },
    participant_id: {
      sourceTable: "participants",
      valueKey: "participant_id",
      apiKey: "participant",
    }
  },
  biobank: {
    participant_sid: {
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
  }
};
