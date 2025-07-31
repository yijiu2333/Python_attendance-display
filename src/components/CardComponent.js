import React from 'react';
import { Card } from 'react-bootstrap';

const CardComponent = ({ 
  title, 
  value, 
  icon, 
  altText,
  bgColor = '#265589',
  textColor = '#fdf5f3',
  shadowColor = 'rgba(10, 9, 60, 0.1)'
}) => {
  return (
    <Card style={{
      backgroundColor: bgColor, 
      color: textColor, 
      boxShadow: `0 4px 6px -11px ${shadowColor}`,
      width: '150px',
      padding: '0.5rem',
      borderRadius: '1rem',
      textAlign: 'center',
      margin: '0.5rem'
    }}>
      <Card.Body>
        <img src={icon} style={{width: '50px', height: 'auto'}} alt={altText} />
        <h4>{title}</h4>
        <h2>{value}</h2>
      </Card.Body>
    </Card>
  );
};

export default CardComponent;