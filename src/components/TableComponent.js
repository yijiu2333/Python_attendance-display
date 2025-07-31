import React from 'react';
import { Table } from 'react-bootstrap';

export default function TableComponent({ data, title }) {
  return (
    <div style={{width: '48%', display: 'inline-block', verticalAlign: 'top'}}>
      <h3>{title}</h3>
      <Table striped bordered hover responsive style={{width: '100%'}}>
        <thead>
          <tr>
            <th style={{minWidth: '100px', textAlign: 'center', backgroundColor: '#D8D7D7'}}>{title.includes('车间') ? '车间' : '部门'}</th>
            <th style={{textAlign: 'center', backgroundColor: '#D8D7D7'}}>应到人数</th>
            <th style={{textAlign: 'center', backgroundColor: '#D8D7D7'}}>实到人数</th>
            <th style={{textAlign: 'center', backgroundColor: '#D8D7D7'}}>出勤率</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} style={{backgroundColor: i % 2 === 0 ? '#E7E7E7' : 'white'}}>
              <td style={{fontWeight: 'bold', color: '#2d3748'}}>{row.department}</td>
              <td style={{textAlign: 'center'}}>{row.expected}</td>
              <td style={{textAlign: 'center'}}>{row.actual}</td>
              <td>
                <div style={{
                  backgroundColor: row.attendance_rate >= 100 ? '#4cb272' : row.attendance_rate >= 70 ? '#f6e05e' : 'red',
                  color: row.attendance_rate >= 100 ? 'white' : '#2d3748',
                  padding: '0.1em',
                  borderRadius: '4px',
                  textAlign: 'center'
                }}>
                  {row.attendance_rate}%
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}