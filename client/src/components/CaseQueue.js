// components/CaseQueue.js

import "../App.css"
import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Button, Table, Spin } from "antd";
import { getIdentifier } from "../utils/schemaAndTables";

export default function CaseQueue({
  selectedRow,
  setSelectedRow,
  onRow,
  queueLoading,
  setQueueLoading,
  openModal
}) {
  const dispatch = useDispatch();
  const caseData =  useSelector((state) => state.data.caseQueue)
  const rows = Array.isArray(caseData) ? caseData[0] : []
  const handleOpen = (schemaKey, record) => {
    if (openModal && record) {
      openModal("edit", { schemaKey, record });
    }
  };
  {queueLoading ? (
      <Spin tip="Loading related case data..." style={{ display: "block", textAlign: "center", marginTop: 20 }}>
        <div style={{ minHeight: 100 }} />
      </Spin>
    ) : (<>div</>)}
  return (
    <>
    <span className="sider-header">
      <Button
        size="small"
        className="action-btn"
        onClick={() => setSelectedRow(null)}
      >Clear</Button>&nbsp;&nbsp;PacBio Case Queue for: {selectedRow.participant_id}&nbsp;&nbsp;
    </span>
    <Table
      className="table"
      dataSource={rows}
      rowKey="participant_id"
      onRow={onRow}
      size="small"
      columns={[
        { title: "Participant ID", key: "participant",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.participant_id || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Analysis status", key: "geneyx_status",
          render: (_, record) => {
            if (!record.geneyx_case.length) return "-";
            return record.geneyx_case["StatusName"]
          }
        },
        { title: "Analyst", key: "created_by",
          render: (_, record) => {
            if (!record.geneyx_case.length) return "-";
            return record.geneyx_case["CreatedByUser"]
          }
        },
        { title: "Second Pass Analyst", key: "modified_by",
          render: (_, record) => {
            if (!record.geneyx_case.length) return "-";
            return record.geneyx_case["ModifiedByUser"]
          }
        },
        { title: "GREGoR Family Size", key: "family size",
          render: (_, record) => {
            return record.family_size
          }
        },
        { title: "LR Case type", key: "lrs_case_type",
          render: (_, record) => {
            return record.gregor_family_structure
          }
        },
        { title: "Date result added", key: "date_created",
          render: (_, record) => {
            if (!record.geneyx_case.length) return "-";
            return record.geneyx_case["CreateDate"]
          }
        },
        { title: "Analysis result from LRS", key: "analysis_result",
          render: (_, record) => {
            if (!record.geneyx_case.length) return "-";
            return record.geneyx_case["SubStatusName"]
          }
        },
        { title: "Relation", dataIndex: "proband_relationship", key: "proband_relationship" },
        { title: "Joint Analysis Status", key: "joint analysis status",
          render: (_, record) => {
            return record.cohort_analysis
          }
        },
        { title: "Gene", key: "gene_of_interest",
          render: (_, record) => {
            const items = Array.isArray(record.genetic_findings) ? record.genetic_findings : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "genetic_findings";
                  const idField = getIdentifier(schemaKey);
                  const label = entry["gene_of_interest"] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        },
        { title: "Variant", key: "hgvsc",
          render: (_, record) => {
            const items = Array.isArray(record.genetic_findings) ? record.genetic_findings : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "genetic_findings";
                  const idField = getIdentifier(schemaKey);
                  const label = entry["hgvsc"] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        },
        { title: "Notes/other notable findings", key: "case_notes",
          render: (_, record) => {
            const items = Array.isArray(record.geneyx_case_notes) ? record.geneyx_case_notes : [];
            if (!items.length) return "-";

            return (
              <div>
                {items.map((entry, index) => {
                  const parser = new DOMParser();
                  const doc = parser.parseFromString(entry["Note"]);
                  const note = doc.body.textContent;
                  return note
                })}
              </div>
            );
          }
        },
        { title: "Sex", key: "sex",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.sex || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Race", key: "reported_race",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.reported_race || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Ethnicity", key: "reported_ethnicity",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.reported_ethnicity || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Age", key: "age_at_enrollment",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.age_at_enrollment || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Phenotype", key: "phenotype_description",
          render: (_, record) => {
            const pheno = record.participant.phenotype_description.toString();
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { pheno || "NA" }
                  </Button>
              </div>
            )
          }
        },
        { title: "Prior Testing", key: "prior_testing",
          render: (_, record) => {
            const prior_testing = record.participant.prior_testing.toString();
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { prior_testing || "NA" }
                  </Button>
              </div>
            )
          }
        },
        { title: "Biobank", key: "biobank",
          render: (_, record) => {
            const items = Array.isArray(record.biobank) ? record.biobank : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "biobank_entries";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        }
      ]}
    />
    </>
  );
}