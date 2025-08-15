// components/ParticipantDetail.js

import "../App.css"
import { useState } from "react";
import { Button, Table, Spin } from "antd";
import { useSelector } from "react-redux";
import { getIdentifier } from "../utils/schemaAndTables";

export default function ParticipantDetail({
  selectedRow,
  setSelectedRow,
  onRow,
  detailLoading,
  setDetailLoding,
  openModal
}) {
  const familyData =  useSelector((state) => state.data.familyDetail)
  const familyName = selectedRow.participant_id
  
  const handleOpen = (schemaKey, record) => {
    if (openModal && record) {
      openModal("edit", { schemaKey, record });
    }
  };
  {detailLoading ? (
      <Spin tip="Loading related family data..." style={{ display: "block", textAlign: "center", marginTop: 20 }}>
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
      >Clear</Button>&nbsp;&nbsp;Family Detail for: {familyName}
    </span>
    <Table
      className="table"
      dataSource={familyData || {}}
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
                    {record.participant.participant_id|| "✓"}
                  </Button>
              </div>
            )
          }
         },
         { title: "Biobank",
          key: "biobank",
          render: (_, record) => {
            const items = record.biobank || [];
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
        { title: "Relation", dataIndex: "proband_relationship", key: "proband_relationship" },
        { title: "Phenotypes",
          key: "pheontypes",
          render: (_, record) => {
            return record.phenotypes.length ? (
              <div>
                {record.phenotypes.map((entry, index) => (
                  <div className="action-btn">
                    <Button
                      key={index}
                      type="link"
                      style={{ padding: 0 }}
                      onClick={() => handleOpen("phenotypes", entry)}
                    >{entry.term_id || "✓"}</Button>
                  </div>
                ))}
              </div>
            ) : "-";
          }
         },
        { title: "Genetic Findings", key: "genetic_findings",
          render: (_, record) => {
            return record.phenotypes.length ? (
              <div>
                {record.genetic_findings.map((entry, index) => (
                  <div className="action-btn">
                    <Button
                      key={index}
                      type="link"
                      style={{ padding: 0 }}
                      onClick={() => handleOpen("genetic_findings", entry)}
                    >{entry.genetic_findings_id || "✓"}</Button>
                  </div>
                ))}
              </div>
            ) : "-";
          }
        },
        { title: "Sequencing", key: "sequencing",
          render: (_, record) => {
            const items = record.sequencing || [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = entry.table_type;
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
        { title: "Alignments", key: "alignments",
          render: (_, record) => {
            const items = record.alignments;
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = entry.table_type;
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
            )
          }
        },
      ]}
    />
    </>
  );
}