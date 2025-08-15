// components/ParticipantDetail.js

import "../App.css"
import { useState } from "react";
import { Button, Table } from "antd";

export default function ParticipantDetail({ selectedRow, setSelectedRow, onRow }) {
  const [detailLoading, setDetailLoding ] = useState(true)
  const familyData = []
  // console.log(familyData)
    
  // {detailLoading ? (
  //     <Spin tip="Loading related family data..." style={{ display: "block", textAlign: "center", marginTop: 20 }}>
  //       <div style={{ minHeight: 100 }} />
  //     </Spin>
  //   ) : (<>div</>)}
  return (
    <>
    <span>
      <Button
        size="small"
        onClick={() => setSelectedRow(null)}
      >Clear</Button>&nbsp;&nbsp;Family Group for: { familyData[0]?.participant_id || "undefined"}
    </span>
    <Table
      className="table"
      dataSource={familyData || {}}
      rowKey="participant_id"
      onRow={onRow}
      size="small"
      // loading={detailLoading}
      columns={[
        { title: "Participant ID", dataIndex: "participant_id", key: "participant_id" },
        { title: "Relation", dataIndex: "proband_relationship", key: "proband_relationship" },
        { title: "Phenotypes", dataIndex: "", key: "pheontypes" },
        { title: "Genetic Findings", key: "genetic_findings",},
        { title: "Sequencing", key: "experiments", },
        { title: "Alignments", key: "alignments",},
      ]}
    />
    </>
  );
}