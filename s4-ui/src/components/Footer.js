import React from 'react';
import { Container } from 'react-bootstrap';

const Footer = () => {
  const year = new Date().getFullYear();
  
  return (
    <footer className="bg-dark text-light py-3 mt-auto">
      <Container className="text-center">
        <p className="mb-0">
          &copy; {year} S4 - Semantic Search Service. All rights reserved.
        </p>
        <p className="small text-muted mb-0">
          Powered by OpenAI, LangChain, and FAISS
        </p>
      </Container>
    </footer>
  );
};

export default Footer; 