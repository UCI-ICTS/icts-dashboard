// src/components/Draggable.js

import React from 'react';
import { useDraggable } from '@dnd-kit/core'

export default function Draggable({id, children, style}) {
  const {attributes, listeners, setNodeRef, transform, isDragging} = useDraggable({ id });
  const dragStyle = transform 
    ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`}
    : undefined;

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      style={{
        cursor: "grab",
        touchAction: "none",
        opacity: isDragging ? .06 : 1,
        ...style,
        ...dragStyle,
      }}
    >
      {children}
    </div>
  );
}