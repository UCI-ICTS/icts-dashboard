import React, { useState, useEffect } from 'react';
import { Card, Input, Button, List, Tag, Radio } from 'antd';
import axios from 'axios';
import moment from 'moment';

const { TextArea } = Input;

const PatientNotes = ({ patientId }) => {
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [isPublic, setIsPublic] = useState(false);

  useEffect(() => {
    fetchNotes();
  }, [patientId]);

  const fetchNotes = async () => {
    try {
      const response = await axios.get(`/api/private/v1/patients/${patientId}/notes/`);
      setNotes(response.data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
  };

  const addNote = async () => {
    if (!newNote.trim()) return;

    try {
      await axios.post(`/api/private/v1/patients/${patientId}/notes/`, {
        content: newNote,
        is_public: isPublic,
      });
      setNewNote('');
      fetchNotes();
    } catch (error) {
      console.error('Error adding note:', error);
    }
  };

  return (
    <Card title="Patient Notes" style={{ width: 300, marginLeft: 16 }}>
      <TextArea
        rows={4}
        value={newNote}
        onChange={(e) => setNewNote(e.target.value)}
        placeholder="Enter your note here..."
      />
      <div style={{ marginTop: 8, marginBottom: 16 }}>
        <Radio.Group
          value={isPublic}
          onChange={(e) => setIsPublic(e.target.value)}
        >
          <Radio value={false}>Private</Radio>
          <Radio value={true}>Public</Radio>
        </Radio.Group>
      </div>
      <Button type="primary" onClick={addNote}>
        Add Note
      </Button>
      <List
        style={{ marginTop: 16 }}
        dataSource={notes}
        renderItem={(note) => (
          <List.Item>
            <List.Item.Meta
              title={
                <span>
                  {moment(note.created_at).format('MMMM D, YYYY, h:mm a')}
                  <Tag color={note.is_public ? 'green' : 'blue'} style={{ marginLeft: 8 }}>
                    {note.is_public ? 'Public' : 'Private'}
                  </Tag>
                </span>
              }
              description={note.content}
            />
          </List.Item>
        )}
      />
    </Card>
  );
};

export default PatientNotes;