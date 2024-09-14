promptUI readme:

---

## **Table of Contents**

1. [Introduction](#introduction)
2. [Overall Architecture](#overall-architecture)
3. [Key Features Breakdown](#key-features-breakdown)
    - [1. JSON Data Management](#1-json-data-management)
    - [2. User Interface Components](#2-user-interface-components)
    - [3. Loading Directory Trees](#3-loading-directory-trees)
    - [4. Adding and Editing Comments](#4-adding-and-editing-comments)
    - [5. Saving Trees to JSON](#5-saving-trees-to-json)
    - [6. Loading Existing Trees from JSON](#6-loading-existing-trees-from-json)
    - [7. Error Handling and User Prompts](#7-error-handling-and-user-prompts)
    - [8. Application Lifecycle Management](#8-application-lifecycle-management)
4. [Workflow Example](#workflow-example)
5. [Future Enhancements](#future-enhancements)
6. [Conclusion](#conclusion)

---

## **Introduction**

The `gui.py` script is a PyQt6-based graphical user interface (GUI) application designed to visualize, annotate, save, and load directory structures. Users can select directories, view their hierarchical structure, add comments to files and folders, and manage multiple such trees with unique titles. All this information is persistently stored in a `trees.json` file, facilitating easy retrieval and management.

---

## **Overall Architecture**

The application is structured around the `Code2PromptGUI` class, which inherits from `QMainWindow`. This class initializes the GUI components, manages user interactions, handles JSON data storage, and ensures seamless loading and saving of directory trees. The core functionalities revolve around:

- **GUI Layout:** Organized using `QVBoxLayout` and `QHBoxLayout` to arrange widgets logically.
- **Tree Visualization:** Utilizes `QTreeWidget` to display directory structures.
- **Data Persistence:** Employs JSON serialization to save and load trees, including their titles and comments.
- **User Interaction:** Facilitates user inputs through dialogs, buttons, and context menus.

---

## **Key Features Breakdown**

Let's delve into each feature, explaining its purpose, implementation, and interaction with other components.

### **1. JSON Data Management**

**Purpose:**  
To persistently store multiple directory trees along with their titles and comments, enabling users to save their work and retrieve it later.

**Implementation:**

- **JSON Structure:**
  
  ```json
  {
    "trees": [
      {
        "title": "Sample Tree",
        "path": "/path/to/directory",
        "root": {
          "name": "directory",
          "type": "directory",
          "comment": "",
          "contents": [
            {
              "name": "subdir",
              "type": "directory",
              "comment": "A subdirectory",
              "contents": [
                {
                  "name": "file.txt",
                  "type": "file",
                  "comment": "A sample file"
                }
              ]
            },
            {
              "name": "file.md",
              "type": "file",
              "comment": "Documentation file"
            }
          ]
        }
      }
      // ... additional trees
    ]
  }
  ```

- **Key Methods:**

  - **`load_trees_data`:**  
    - **Function:** Loads existing tree data from `trees.json`.
    - **Process:**  
      - Checks if `trees.json` exists.
      - If it exists, attempts to parse the JSON content into `self.trees_data`.
      - If parsing fails (e.g., due to corruption), initializes an empty structure and notifies the user.
      - If the file doesn't exist, initializes `self.trees_data` with an empty `"trees"` array.

  - **`save_trees_data`:**  
    - **Function:** Writes the current `self.trees_data` back to `trees.json`.
    - **Process:**  
      - Serializes `self.trees_data` using `json.dump` with indentation for readability.
      - Handles any exceptions during the write process, notifying the user if issues arise.

**Interaction with Other Components:**  
These methods are foundational, ensuring that all tree operations (load/save) interact seamlessly with the persistent storage.

### **2. User Interface Components**

**Purpose:**  
To provide an intuitive and organized layout for users to interact with the application, including selecting directories, viewing trees, adding comments, and managing saved trees.

**Implementation:**

- **Layout Structure:**
  
  - **Main Layout (`QVBoxLayout`):**  
    Organizes all components vertically.
  
  - **Top Layout (`QHBoxLayout`):**  
    Contains the tree title input and the dropdown to load existing trees.
  
  - **Path Selection Layout (`QHBoxLayout`):**  
    Includes the directory path input, "Browse" button, and "Load Tree" button.
  
  - **Tree Widget (`QTreeWidget`):**  
    Displays the hierarchical directory structure with columns for Name, Type, and Comment.
  
  - **Save Button Layout (`QHBoxLayout`):**  
    Houses the "Save Tree" button, aligned to the right.

- **Key Widgets:**

  - **`QLineEdit` for Tree Title (`self.title_input`):**  
    Allows users to input a unique title for the current tree.

  - **`QComboBox` for Loading Existing Trees (`self.load_combo`):**  
    Lists all saved tree titles from `trees.json` for easy selection and loading.

  - **`QLineEdit` for Directory Path (`self.path_input`):**  
    Enables users to enter or display the path of the directory they wish to visualize.

  - **`QPushButton` for Browsing Directories (`browse_button`):**  
    Opens a directory selection dialog to choose a directory visually.

  - **`QPushButton` for Loading Trees (`load_button`):**  
    Initiates the process of loading and displaying the directory tree based on the provided path.

  - **`QTreeWidget` (`self.tree_widget`):**  
    Renders the directory structure in a tree format, allowing for expansion, collapsing, and annotation via comments.

  - **`QPushButton` for Saving Trees (`self.save_button`):**  
    Saves the current tree structure, along with its title and comments, to `trees.json`.

- **Context Menu for Comments:**
  
  - **`QMenu`:**  
    Activated on right-clicking a tree item, offering the "Add/Edit Comment" option.

  - **`QInputDialog`:**  
    Pops up to allow users to input or modify comments for selected tree items.

**Interaction with Other Components:**  
These widgets and layouts are interconnected to facilitate seamless user interactions, such as loading trees, adding comments, and saving data.

### **3. Loading Directory Trees**

**Purpose:**  
To visualize the structure of a selected directory in the `QTreeWidget`, enabling users to navigate and annotate their filesystem.

**Implementation:**

- **Methods Involved:**

  - **`browse_directory`:**  
    - **Function:** Opens a dialog for users to select a directory.
    - **Process:**  
      - Utilizes `QFileDialog.getExistingDirectory` to let users pick a directory.
      - Updates `self.path_input` with the selected directory path.

  - **`load_tree_from_path`:**  
    - **Function:** Loads and displays the directory structure in the `QTreeWidget`.
    - **Process:**  
      - Retrieves the directory path from `self.path_input`.
      - Validates the path (ensures it exists and is a directory).
      - Clears any existing tree in `self.tree_widget`.
      - Creates a root `QTreeWidgetItem` representing the selected directory.
      - Calls `populate_tree` to recursively add child items (subdirectories and files).

  - **`populate_tree`:**  
    - **Function:** Recursively populates the `QTreeWidget` with the contents of the directory.
    - **Process:**  
      - Iterates over the contents of the given `path`.
      - Sorts items to display directories before files, sorted alphabetically.
      - For each directory, creates a child `QTreeWidgetItem` and recursively calls itself to populate its contents.
      - For each file, creates a child `QTreeWidgetItem`.
      - Handles `PermissionError` and other exceptions by adding placeholder items indicating issues.

**Interaction with Other Components:**  
This feature interacts closely with the JSON data management system. When a tree is loaded from a directory, it can be annotated and subsequently saved to JSON for future retrieval.

### **4. Adding and Editing Comments**

**Purpose:**  
To allow users to annotate specific files or directories with comments, enhancing the descriptive value of each tree.

**Implementation:**

- **Context Menu Activation:**
  
  - **`open_context_menu`:**  
    - **Function:** Detects right-clicks on tree items and opens a context menu.
    - **Process:**  
      - Identifies the item under the cursor.
      - Creates a `QMenu` with an "Add/Edit Comment" option.
      - Connects this option to the `edit_comment` method.

- **Editing Comments:**
  
  - **`edit_comment`:**  
    - **Function:** Opens an input dialog to allow users to add or modify comments.
    - **Process:**  
      - Retrieves the current comment from the third column of the selected item.
      - Uses `QInputDialog.getText` to prompt the user for a new comment, pre-filled with the existing one.
      - If the user confirms, updates the third column with the new comment.

**Interaction with Other Components:**  
Comments are stored within the `QTreeWidget` and are later serialized into the JSON structure when saving the tree. This ensures that annotations persist across sessions.

### **5. Saving Trees to JSON**

**Purpose:**  
To persistently store the current tree structure, including titles and comments, in `trees.json` for future retrieval and management.

**Implementation:**

- **`save_tree`:**  
  - **Function:** Saves the current tree to `trees.json`.
  - **Process:**
    1. **Retrieve Title:**
       - Gets the title from `self.title_input`.
    2. **Handle Missing Title:**
       - If no title is provided, prompts the user to confirm auto-generating one with a timestamp.
       - Generates a title in the format `"Untitled_MM-DD-YY-HH-MM-SS"`.
    3. **Check for Duplicate Titles:**
       - Scans existing titles in `self.trees_data` to ensure uniqueness.
       - If a duplicate is found, warns the user and aborts the save operation.
    4. **Retrieve Root Item:**
       - Gets the top-level item from `self.tree_widget`.
       - If no tree is loaded, warns the user.
    5. **Build JSON Representation:**
       - Calls `build_tree_json` to convert the tree structure into a JSON-compatible dictionary.
       - Constructs a `tree_json` dictionary with `title`, `path`, and `root`.
    6. **Update `trees_data`:**
       - Appends the new `tree_json` to the `trees` array in `self.trees_data`.
    7. **Save to JSON File:**
       - Calls `save_trees_data` to write the updated data back to `trees.json`.
    8. **Update Load Dropdown:**
       - Adds the new title to `self.load_combo` for future loading.
    9. **User Notification:**
       - Informs the user that the tree has been saved successfully.

- **`build_tree_json`:**  
  - **Function:** Converts a `QTreeWidgetItem` and its children into a nested dictionary suitable for JSON serialization.
  - **Process:**  
    - Extracts the `name`, `type`, and `comment` from the item's columns.
    - If the item has children (i.e., it's a directory), recursively calls itself to build the `contents` array.
    - Returns the constructed node dictionary.

**Interaction with Other Components:**  
Upon saving, the tree's data is serialized into JSON and stored in `trees.json`, ensuring that titles and comments are preserved. This allows users to retrieve and manage their annotated trees seamlessly.

### **6. Loading Existing Trees from JSON**

**Purpose:**  
To retrieve and display previously saved trees from `trees.json`, allowing users to revisit and modify their annotations.

**Implementation:**

- **`load_selected_tree`:**  
  - **Function:** Loads a selected tree from the JSON data and displays it in the `QTreeWidget`.
  - **Process:**  
    1. **Check Selection:**
       - Ignores the placeholder selection (`"-- Select Existing Tree --"`).
    2. **Retrieve Selected Title:**
       - Gets the current text from `self.load_combo`.
    3. **Find Tree in JSON:**
       - Searches `self.trees_data['trees']` for a tree matching the selected title.
    4. **Handle Missing Tree:**
       - If no matching tree is found, warns the user.
    5. **Set Inputs:**
       - Updates `self.title_input` and `self.path_input` with the loaded tree's title and path.
    6. **Clear Existing Tree:**
       - Clears any existing tree in `self.tree_widget`.
    7. **Populate Tree Widget:**
       - Extracts the `root` dictionary from the loaded tree.
       - Creates a root `QTreeWidgetItem` with the root's `name`, `type`, and `comment`.
       - Calls `populate_tree_from_json` to recursively add child items based on the JSON structure.
       - Expands the root item for visibility.
    8. **Error Handling:**
       - Catches and notifies the user of any exceptions during the loading process.

- **`populate_tree_from_json`:**  
  - **Function:** Recursively adds tree items to the `QTreeWidget` based on the JSON data.
  - **Process:**  
    - Extracts the `contents` array from the current JSON node.
    - For each child:
      - Retrieves `name`, `type`, and `comment`.
      - Creates a `QTreeWidgetItem` with these details.
      - Adds it as a child to the parent item.
      - If the child is a directory, recursively calls itself to add its contents.

**Interaction with Other Components:**  
This feature enables users to effortlessly switch between different saved trees, viewing and editing their annotations as needed.

### **7. Error Handling and User Prompts**

**Purpose:**  
To ensure robustness and a smooth user experience by handling potential errors and guiding users through necessary confirmations.

**Implementation:**

- **JSON Parsing Errors:**
  
  - **Scenario:** `trees.json` is corrupted or improperly formatted.
  
  - **Handling:**  
    - Catches `json.JSONDecodeError` during `load_trees_data`.
    - Notifies the user via a critical message box.
    - Initializes an empty `trees_data` structure to prevent crashes.

- **Duplicate Titles:**
  
  - **Scenario:** User attempts to save a tree with a title that already exists.
  
  - **Handling:**  
    - Checks for existing titles in `save_tree`.
    - If a duplicate is found, warns the user and aborts the save operation.

- **Missing Directory Path:**
  
  - **Scenario:** User tries to load a tree without specifying a directory path.
  
  - **Handling:**  
    - Prompts a warning message urging the user to provide a valid path.

- **Permission Errors:**
  
  - **Scenario:** Application lacks permissions to access certain directories.
  
  - **Handling:**  
    - Adds placeholder items like `[Permission Denied]` in the tree view.
    - Prevents the application from crashing due to unhandled exceptions.

- **Auto-Generating Titles:**
  
  - **Scenario:** User saves a tree without providing a title.
  
  - **Handling:**  
    - Prompts the user to confirm auto-generating a title.
    - Generates a unique title using the current timestamp.

- **Application Closure:**
  
  - **Scenario:** User attempts to close the application.
  
  - **Handling:**  
    - Prompts the user to confirm quitting.
    - Allows users to cancel the close operation if they choose.

**Interaction with Other Components:**  
Error handling mechanisms are integrated throughout various methods to ensure that users are always informed of issues and guided on how to resolve them, maintaining application stability.

### **8. Application Lifecycle Management**

**Purpose:**  
To manage the behavior of the application during startup and shutdown, ensuring data integrity and user confirmation upon exit.

**Implementation:**

- **Initialization:**
  
  - **`__init__`:**  
    - Sets up the GUI layout and initializes data structures.
    - Loads existing trees from `trees.json` to populate the load dropdown.

- **Closure:**
  
  - **`closeEvent`:**  
    - Overrides the default close event.
    - Prompts the user to confirm quitting the application.
    - Allows users to cancel the close operation, preventing accidental exits.

**Interaction with Other Components:**  
Ensures that data is correctly loaded upon startup and that users are given a chance to confirm their intent to close the application, preventing unintended data loss.

---

## **Workflow Example**

To solidify understanding, let's walk through a typical user interaction scenario, illustrating how different components and features work together.

### **1. Starting the Application**

- **Action:**  
  - User launches the application by running `gui.py`.
  
- **Process:**  
  - `Code2PromptGUI` initializes.
  - `load_trees_data` reads `trees.json` (if it exists) and populates `self.load_combo` with existing tree titles.

- **Result:**  
  - GUI window appears with input fields for tree title and directory path, dropdown for existing trees, tree view, and save button.

### **2. Loading a Directory Tree**

- **Action:**  
  - User clicks the "Browse" button to select a directory or manually enters a directory path in `self.path_input`.
  - Clicks "Load Tree" to visualize the directory structure.

- **Process:**  
  - `load_tree_from_path` validates the directory path.
  - Clears any existing tree in `self.tree_widget`.
  - Creates a root `QTreeWidgetItem` representing the selected directory.
  - Calls `populate_tree` to recursively add subdirectories and files.
  - Tree view displays the directory hierarchy.

- **Result:**  
  - Users see the directory structure in the tree view, ready for annotation.

### **3. Adding Comments**

- **Action:**  
  - User right-clicks on a directory or file within the tree view.
  - Selects "Add/Edit Comment" from the context menu.
  - Enters a comment in the input dialog.

- **Process:**  
  - `open_context_menu` detects the right-click and opens the menu.
  - `edit_comment` retrieves the current comment and prompts the user for a new one.
  - Updates the comment in the tree view.

- **Result:**  
  - The selected item now displays the user-provided comment in the third column.

### **4. Saving the Tree**

- **Action:**  
  - User enters a unique title in the "Tree Title" input field.
  - Clicks "Save Tree" to persist the current tree structure.

- **Process:**  
  - `save_tree` retrieves the title and validates uniqueness.
  - If no title is provided, prompts for auto-generation.
  - Calls `build_tree_json` to convert the tree into a JSON-compatible dictionary.
  - Appends the new tree to `self.trees_data['trees']`.
  - Calls `save_trees_data` to write the updated data to `trees.json`.
  - Updates `self.load_combo` with the new title.
  - Notifies the user of successful save.

- **Result:**  
  - The tree is saved in `trees.json` with the provided title, path, and comments.

### **5. Loading an Existing Tree**

- **Action:**  
  - User selects a saved tree title from the "Load Existing Tree" dropdown.

- **Process:**  
  - `load_selected_tree` retrieves the corresponding tree data from `self.trees_data`.
  - Sets the title and path input fields based on the loaded tree.
  - Clears the current tree view.
  - Calls `populate_tree_from_json` to reconstruct the tree structure with comments from JSON.
  - Expands the root item for visibility.

- **Result:**  
  - The selected tree is displayed in the tree view, complete with all comments.

### **6. Handling Duplicate Titles**

- **Action:**  
  - User attempts to save another tree with a title that already exists in `trees.json`.

- **Process:**  
  - `save_tree` detects the duplicate title during the save operation.
  - Warns the user via a message box.
  - Aborts the save process, preventing overwriting.

- **Result:**  
  - User is informed of the duplicate and can choose to provide a different title.

### **7. Exiting the Application**

- **Action:**  
  - User attempts to close the application window.

- **Process:**  
  - `closeEvent` intercepts the close action.
  - Prompts the user to confirm quitting.
  - If the user confirms, the application closes.
  - If the user cancels, the application remains open.

- **Result:**  
  - Controlled and intentional application closure, safeguarding against accidental exits.

---

## **Future Enhancements**

While the current implementation provides robust functionality, several enhancements can further elevate the user experience and expand capabilities:

1. **Editing Existing Trees:**
   - **Feature:** Allow users to modify the title of an existing tree.
   - **Implementation:**  
     - Detect changes in `self.title_input`.
     - Prompt users to confirm whether to overwrite the existing tree or create a new one.
     - Update `trees.json` accordingly.

2. **Deleting Trees:**
   - **Feature:** Enable users to remove unwanted trees from `trees.json`.
   - **Implementation:**  
     - Add a "Delete Tree" button.
     - Upon selection, remove the tree from `self.trees_data['trees']` and update `trees.json`.

3. **Exporting and Importing Trees:**
   - **Feature:** Allow users to export individual trees as separate JSON files and import them as needed.
   - **Implementation:**  
     - Use `QFileDialog` to select export/import file paths.
     - Serialize and deserialize tree data accordingly.

4. **Search Functionality:**
   - **Feature:** Implement a search bar to locate specific files or directories within the tree.
   - **Implementation:**  
     - Add a `QLineEdit` for search input.
     - Traverse `self.tree_widget` items to highlight matches.

5. **Visual Enhancements:**
   - **Feature:** Use icons to differentiate between files and directories visually.
   - **Implementation:**  
     - Assign appropriate icons to `QTreeWidgetItem` based on their type.

6. **Backup Mechanism:**
   - **Feature:** Automatically create backups of `trees.json` to prevent data loss.
   - **Implementation:**  
     - Before writing to `trees.json`, copy its current state to a backup file with a timestamp.

7. **Integration with Code2Prompt:**
   - **Feature:** Connect the GUI with the `Code2Prompt` backend for tasks like code analysis or documentation generation.
   - **Implementation:**  
     - Define methods to invoke `Code2Prompt` functionalities based on user interactions within the GUI.

8. **User Preferences and Settings:**
   - **Feature:** Allow users to customize aspects like default directory paths, display options, or comment styles.
   - **Implementation:**  
     - Use `QSettings` or a similar mechanism to store user preferences.

---

## **Conclusion**

The `gui.py` implementation serves as a powerful tool for visualizing and managing directory structures with added annotations. By leveraging PyQt6's robust GUI components and JSON's flexibility for data storage, the application offers a user-friendly interface for organizing and documenting file systems. This detailed breakdown elucidates how each feature is meticulously crafted to interact harmoniously, ensuring both functionality and user experience are paramount.

As we continue to develop and enhance the application, keeping this structured understanding at hand will facilitate smoother integrations, troubleshooting, and feature expansions. Should we embark on adding more complex functionalities or refining existing ones, refer back to this guide to maintain coherence and consistency within the codebase.

