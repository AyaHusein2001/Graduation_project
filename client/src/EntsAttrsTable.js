// import React, { useState } from 'react';
// import { IoMdClose } from 'react-icons/io';
// import './EntsAttrsTable.css'; // Assuming you have a CSS file for styling

// const EntsAttrsTable = ({ entitiesWithAttr, entitiesWithPks, relationships }) => {
//   const [entities, setEntities] = useState(entitiesWithAttr);

//   const handleDelete = (entity, attr) => {
//     setEntities((prevEntities) => ({
//       ...prevEntities,
//       [entity]: prevEntities[entity].filter((attribute) => attribute !== attr),
//     }));
//   };

//   const handleAdd = (entity, newAttr) => {
//     if (newAttr) {
//       setEntities((prevEntities) => ({
//         ...prevEntities,
//         [entity]: [...prevEntities[entity], newAttr],
//       }));
//     }
//   };

//   const isEmptyObject = (obj) => Object.keys(obj).length === 0;

//   const isPrimaryKey = (entity, attr) => {
//     return entitiesWithPks[entity] === attr;
//   };

//   const isForeignKey = (entity, attr) => {
//     return relationships.some(rel => 
//       (rel[1] === entity && rel[2] === 'many' && rel[3] === '1' && rel[4] === attr) || 
//       (rel[1] === '1' && rel[3] === entity && rel[4] === attr)
//     );
//   };

//   return (
//     <div>
//       <h2>Entities with Attributes</h2>
//       {isEmptyObject(entities) ? (
//         <p>No entities with attributes found</p>
//       ) : (
//         <ul>
//           {Object.keys(entities).map((entity, index) => (
//             <li key={index}>
//               <div>
//                 <strong>{entity}</strong>:
//                 <div className="attributes-row">
//                   {entities[entity].map((attr, attrIndex) => (
//                     <div 
//                       className={`attribute ${isPrimaryKey(entity, attr) ? 'primary-key' : ''} ${isForeignKey(entity, attr) ? 'foreign-key' : ''}`} 
//                       key={attrIndex}
//                     >
//                       {attr} {isPrimaryKey(entity, attr) ? '(pk)' : ''} {isForeignKey(entity, attr) ? '(fk)' : ''}
//                       {!isPrimaryKey(entity, attr) && !isForeignKey(entity, attr) && (
//                         <IoMdClose
//                           className="close-icon"
//                           onClick={() => handleDelete(entity, attr)}
//                         />
//                       )}
//                     </div>
//                   ))}
//                 </div>
//                 <div className="add-attribute">
//                   <input
//                     type="text"
//                     placeholder="New attribute"
//                     onKeyDown={(e) => {
//                       if (e.key === 'Enter') {
//                         handleAdd(entity, e.target.value);
//                         e.target.value = '';
//                       }
//                     }}
//                   />
//                   <button
//                     onClick={(e) => {
//                       const input = e.target.previousSibling;
//                       handleAdd(entity, input.value);
//                       input.value = '';
//                     }}
//                   >
//                     Add
//                   </button>
//                 </div>
//               </div>
//             </li>
//           ))}
//         </ul>
//       )}
//     </div>
//   );
// };

// export default EntsAttrsTable;

import React, { useState } from 'react';
import { IoMdClose } from 'react-icons/io';
import './EntsAttrsTable.css'; // Assuming you have a CSS file for styling

const EntsAttrsTable = ({ entitiesWithAttr, entitiesWithPks, relationships }) => {
  const [entities, setEntities] = useState(entitiesWithAttr);

  const handleDelete = (entity, attr) => {
    setEntities((prevEntities) => ({
      ...prevEntities,
      [entity]: prevEntities[entity].filter((attribute) => attribute !== attr),
    }));
  };

  const handleAdd = (entity, newAttr) => {
    if (newAttr) {
      setEntities((prevEntities) => ({
        ...prevEntities,
        [entity]: [...prevEntities[entity], newAttr],
      }));
    }
  };

  const isEmptyObject = (obj) => Object.keys(obj).length === 0;

  const isPrimaryKey = (entity, attr) => {
    return entitiesWithPks[entity] === attr;
  };

  const isForeignKey = (entity, attr) => {
    return relationships.some(rel => 
      (rel[1] === entity && rel[2] === 'many' && rel[3] === '1' && rel[4] === attr) || 
      (rel[1] === '1' && rel[3] === entity && rel[4] === attr)
    );
  };

  return (
    <div>
      <h2>Entities with Attributes</h2>
      {isEmptyObject(entities) ? (
        <p>No entities with attributes found</p>
      ) : (
        <ul>
          {Object.keys(entities).map((entity, index) => (
            <li key={index}>
              <div>
                <strong>{entity}</strong>:
                <div className="attributes-row">
                  {entities[entity].map((attr, attrIndex) => (
                    <div 
                      className={`attribute ${isPrimaryKey(entity, attr) ? 'primary-key' : ''} ${isForeignKey(entity, attr) ? 'foreign-key' : ''}`} 
                      key={attrIndex}
                    >
                      {attr} {isPrimaryKey(entity, attr) ? '(pk)' : ''} {isForeignKey(entity, attr) ? '(fk)' : ''}
                      {!isPrimaryKey(entity, attr) && !isForeignKey(entity, attr) && (
                        <IoMdClose
                          className="close-icon"
                          onClick={() => handleDelete(entity, attr)}
                        />
                      )}
                    </div>
                  ))}
                </div>
                <div className="add-attribute">
                  <input
                    type="text"
                    placeholder="New attribute"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleAdd(entity, e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={(e) => {
                      const input = e.target.previousSibling;
                      handleAdd(entity, input.value);
                      input.value = '';
                    }}
                  >
                    Add
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default EntsAttrsTable;
