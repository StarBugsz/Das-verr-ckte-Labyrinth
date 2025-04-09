import React from 'react';
import "../index.css";

//Page Containter war benötigt um im nachhinein die font besser anzupassen
function PageContainer({ children }) {
    return (
        <div className="page-container">
            {children}
        </div>
    );
}

export default PageContainer;
