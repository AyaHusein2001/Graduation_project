# Webby: A Machine Learning-Powered Website Development Tool 🚀

## Abstract 📋
The Webby project is a groundbreaking approach to website development, designed to cater to users with limited IT expertise. Leveraging machine learning and natural language processing (NLP), Webby translates user requirements, articulated in natural language, into functional website components in real-time. The frontend development team focused on creating an intuitive and visually appealing interface using modern web technologies. Meanwhile, the backend team extracted essential database components from user descriptions, generating SQL queries and backend CRUD operations using Django. These combined efforts result in a comprehensive solution that simplifies website development while ensuring robust backend functionality and data integrity.

## Feasibility Study 🔍

### Module 1: Data Gathering and Preprocessing 🗃️
- **Objective:** Create a unique dataset of website templates.
- **Feasibility:** Manageable through manual collection and description formulation, supported by efficient team distribution.

### Module 2: Classification & Retrieval 🔍
- **Objective:** Classify user input descriptions and retrieve matching templates.
- **Feasibility:** Achievable with available machine learning tools, cosine similarity, and word embeddings.

### Module 3: Generation 🛠️
- **Objective:** Dynamically modify HTML content based on user inputs and automate CSS color changes.
- **Feasibility:** Supported by existing libraries and frameworks like Material UI.

### Module 4: Entities and Attributes Extraction 📊
- **Objective:** Extract entities and attributes from user text inputs using BiLSTM models.
- **Feasibility:** Technically feasible with appropriate data preprocessing and model training.

### Module 5: Relationship and Cardinalities Extraction 🔗
- **Objective:** Identify relationships and cardinalities between entities.
- **Feasibility:** Manageable with robust algorithms and clear data structuring techniques.

### Module 6: Entities with Attributes Association and Primary Keys Extraction 🔑
- **Objective:** Extract primary keys and associate entities with attributes.
- **Feasibility:** Technically feasible with well-defined workflows and comprehensive reference databases.

### Module 7: Reference Database Construction 🗄️
- **Objective:** Construct a reference database from SQL query files.
- **Feasibility:** Technically feasible through preprocessing of SQL queries and extraction using regular expressions.

### Module 8: SQL Queries Generation 📝
- **Objective:** Generate SQL queries based on extracted entities, attributes, relationships, and primary keys.
- **Feasibility:** Supported by SQL query templates and execution in SQLite3.

### Module 9: Django Script Setup and Management 🛠️
- **Objective:** Set up and manage the Django project, including initialization, database management, and server launch.
- **Feasibility:** Feasible with established Django practices and guidelines.

### Module 10: Project Website Builder Frontend and Backend Development 🌐
- **Objective:** Develop a user-friendly project website with a responsive frontend and robust backend integration.
- **Feasibility:** Achievable using React.js for frontend development, Node.js for backend development, and seamless integration using Material UI.

## User Guide 📖

### Steps for Database and GUI Description

1. **Database Description:**
   - In the "Database Description" textbox, describe the details of your website's database.
   - Provide this description as if explaining it to a specialist who will create the database for you.
   - Specify the names of the tables you want and list the columns for each table.

2. **GUI Description:**
   - In the "GUI Description" textbox, describe the customizations you want for your website's interface, including styling details.
   - Click the "Open Color Picker" button to choose the main color of your website.
   - After selecting the color, click the "Submit" button.

3. **Table Names Confirmation:**
   - The system will detect the table names from your database description input.
   - You can add more tables in the "New Table" text field or delete existing tables by clicking the delete icon next to the table name.

4. **Final Schema Review:**
   - The system will display a list of your final database tables along with their columns (including extra columns provided by the system).
   - You can accept this as the final schema or make further modifications by adding or deleting columns for any table.

5. **Finalizing and Downloading:**
   - Once you have finalized the schema, press "OK" to complete the setup.
   - The system will provide a link to download your website with the specified customizations.
   - Download the folder and open it.

6. **Running the Website:**
   - Open the command line in the downloaded folder.
   - Run the command `python manage.py runserver`.
   - Follow the link provided in the command line to access your website.
   - Append "/admin" to the URL to access the admin interface, where you can manage your database entries (insert, read, delete, update) as the website owner.

## Development Platforms and Tools 💻

### Hardware Platforms
- **Google Colab:** Used for cloud-based training, especially for backend development.

### Software Tools
- **Python:** Main programming language for building the library.

### Main Libraries
- **re:** Performing regular expression operations.
- **nltk:** Natural language processing tasks, including tokenization and stemming.
- **stanza:** NLP tasks such as tokenization, part-of-speech tagging, lemmatization, and dependency parsing.
- **sklearn.metrics:** Calculating metrics like accuracy score.
- **sklearn:** Methods for classification.
- **tensorflow.keras.preprocessing.sequence.pad_sequences:** Padding sequences to ensure uniform length.

### Tools and Platforms
- **Visual Studio Code:** For editing code while building the project.
- **Jupyter Notebook:** For demonstration purposes and testing.

---

We hope Webby makes website development easier and more accessible for everyone! 🚀🌐
