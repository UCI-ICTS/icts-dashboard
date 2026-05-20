// components/CaseQueue.js

import "../App.css"
import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Button, Table, Spin } from "antd";
import { getIdentifier } from "../utils/schemaAndTables";
import { getSamples } from "../slices/geneyxSlice";

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
      <Button
        size="small"
        className="action-btn"
        onClick={() => {let response = dispatch(getSamples()); console.log({response});}}
      >Get Geneyx Samples</Button>
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
        { title: "Analysis status", key: "family size",
          render: (_, record) => {
            return record.family_size
          }
        },
        { title: "Analyst", key: "family size",
          render: (_, record) => {
            return record.family_size
          }
        },
        { title: "Second Pass Analyst", key: "family size",
          render: (_, record) => {
            return record.family_size
          }
        },
        { title: "GREGoR Family Size", key: "family size",
          render: (_, record) => {
            return record.family_size
          }
        },
        { title: "LR Case type", key: "family size",
          render: (_, record) => {
            return record.gregor_family_structure
          }
        },
        { title: "Date result added", key: "family size",
          render: (_, record) => {
            return record.family_size
          }
        },
        { title: "Analysis result from LRS", key: "family size",
          render: (_, record) => {
            return record.family_size
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
        { title: "Notes/other notable findings", key: "family size",
          render: (_, record) => {
            return record.family_size
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
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.phenotype_description || "NA"}
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
                  const label = entry[idField] ||  "✓";
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
        { title: "Analytes", key: "analytes",
          render: (_, record) => {
            const items = Array.isArray(record.sequencing) ? record.analytes : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "analytes";
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
        },
        { title: "Sequencing", key: "sequencing",
          render: (_, record) => {
            const items = Array.isArray(record.sequencing) ? record.sequencing : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "experiment_pac_bio";
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
        },
        { title: "Alignments", key: "alignments",
          render: (_, record) => {
            const items = Array.isArray(record.alignments) ? record.alignments : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "aligned_pac_bio";
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
            )
          }
        }
      ]}
    />
    </>
  );
}