// src/components/Droppable.js

import React from "react";
import { useDroppable } from "@dnd-kit/core";

export default function Droppable({id, children, style}) {
    const { setNodeRef, isOver } = useDroppable({ id });
    return (
        <div
          ref={setNodeRef}
          style={{
            minHeight: 120,  //Empty columns mus have height
            padding: 8,
            borderRadius: 8,
            border: "1px dashed #ccc",
            background: isOver ? "#fafafa" : "transparent",
            ...style
          }}
        >
          {children}
        </div>
    )
 }