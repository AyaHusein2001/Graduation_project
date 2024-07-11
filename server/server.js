const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');

const app = express();
const port = 3001;

app.use(bodyParser.json());

app.post('/save', (req, res) => {
  const { entitiesWithAttr, entitiesWithPKs, relationships } = req.body;
  const inputData = JSON.stringify({
    entities_with_attr: entitiesWithAttr,
    entities_with_pks: entitiesWithPKs,
    relationships: relationships
  });
  console.log(inputData)
  

  const pythonProcess = spawn('python', ['create_admin.py', inputData]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    res.sendStatus(200);
  });
});

app.post('/process-text', (req, res) => {
  const { text } = req.body;
  const pythonProcess = spawn('python', ['entities_extract.py', text]);

  let stdoutData = '';
  let stderrData = '';

  pythonProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
  });

  pythonProcess.on('close', (code) => {
      if (code !== 0) {
          console.error(`Python process exited with code ${code}`);
          console.error(`stderr: ${stderrData}`);
          return res.status(500).send('Error processing text');
      }

      // Extract JSON part from stdoutData
      let jsonData;
      try {
        console.log(stdoutData)

          // Find the last occurrence of '[' in stdoutData
          const lastBracketIndex = stdoutData.lastIndexOf('[');
          if (lastBracketIndex === -1) {
              throw new Error('No JSON array found in the output');
          }
          // Get the substring starting from the last occurrence of '['
          const jsonString = stdoutData.substring(lastBracketIndex);
          jsonData = JSON.parse(jsonString);
      } catch (err) {
        console.log(stdoutData)
          console.error(`Failed to parse JSON: ${err}`);
          console.error(`Output: ${stdoutData}`);
          return res.status(500).send('Error processing text');
      }

      res.json({ result: jsonData });
  });
});

app.post('/process-data', (req, res) => {
  const { description, entities } = req.body;
  const inputData = JSON.stringify({ description, entities });

  const pythonProcess = spawn('python', ['backend.py', inputData]);

  let stdoutData = '';
  let stderrData = '';

  pythonProcess.stdout.on('data', (data) => {
    stdoutData += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    stderrData += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`Python process exited with code ${code}`);
      console.error(`stderr: ${stderrData}`);
      return res.status(500).send('Error processing data');
    }

    let jsonData;
    try {
      console.log(`stdout: ${stdoutData}`);
      console.error(`stderr: ${stderrData}`);

      // Extract JSON from stdout using a regular expression
      const jsonStringMatch = stdoutData.match(/{[\s\S]*}/);
      if (!jsonStringMatch) {
        throw new Error('No JSON found in output');
      }
      
      jsonData = JSON.parse(jsonStringMatch[0]);
    } catch (err) {
      console.error(`Failed to parse JSON: ${err}`);
      console.error(`Output: ${stdoutData}`);
      return res.status(500).send('Error processing data');
    }

    res.json(jsonData);
  });
});

app.post('/process-elements', (req, res) => {
  const { elements } = req.body;
  const pythonProcess = spawn('python', ['process_elements.py', JSON.stringify(elements)]);

  pythonProcess.stdout.on('data', (data) => {
    const result = JSON.parse(data.toString());
    res.json(result);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
    res.status(500).send('Error processing elements');
  });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
