import React, { useState } from 'react';
import { ChromePicker } from 'react-color';

const ColorPicker = ({ onColorChange }) => {
  const [color, setColor] = useState('#ffffff');

  const handleColorChange = (selectedColor) => {
    const newColor = selectedColor.hex;
    setColor(newColor);
    onColorChange(newColor); // Call the parent callback with the selected color
  };

  return (
    <div>
      <ChromePicker color={color} onChange={handleColorChange} />
      <p>Selected Color: {color}</p>
    </div>
  );
};

export default ColorPicker;
