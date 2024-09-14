# promptUI: A GUI for creating and managing prompts

---

## Table of Contents

1. [Introduction](#introduction)
2. [Overall Architecture](#overall-architecture)
3. [Key Features Breakdown](#key-features-breakdown)
    - [1. Modular Code Structure](#1-modular-code-structure)
    - [2. JSON Data Management](#2-json-data-management)
    - [3. User Interface Components](#3-user-interface-components)
    - [4. Loading Directory Trees](#4-loading-directory-trees)
    - [5. Adding and Editing Comments](#5-adding-and-editing-comments)
    - [6. Command Builder Integration](#6-command-builder-integration)
    - [7. Saving and Loading Trees](#7-saving-and-loading-trees)
    - [8. Error Handling and User Prompts](#8-error-handling-and-user-prompts)
    - [9. Application Lifecycle Management](#9-application-lifecycle-management)
4. [Workflow Example](#workflow-example)
5. [Future Enhancements](#future-enhancements)
6. [Conclusion](#conclusion)

---

## Introduction

**promptUI** is a PyQt6-based graphical user interface (GUI) application designed to visualize, annotate, and manage directory structures interactively. Users can select directories, view their hierarchical structures, add comments to files and folders, filter or exclude specific items, and dynamically build commands for the `code2prompt` tool based on their selections. The application supports saving and loading multiple annotated trees, facilitating efficient project management and documentation.

---

## Overall Architecture

The application is structured into modular components, each handling specific functionalities, promoting maintainability and scalability. The key modules are:

- **`main.py`**: The entry point of the application.
- **`main_window.py`**: Manages the main application window and integrates all components.
- **`tree_view.py`**: Handles the directory tree visualization and user interactions with tree items.
- **`tree_item.py`**: Defines a custom tree item class with additional attributes like comments and filter states.
- **`details_panel.py`**: Provides an interface for viewing and editing comments on selected items.
- **`command_builder.py`**: Dynamically constructs the `code2prompt` command based on user selections.
- **`data_manager.py`**: Manages the saving and loading of tree data to and from JSON files.
- **`utils.py`**: Contains utility functions used across the application.

The modular design allows for focused development on individual components and facilitates easier testing and maintenance.

---

## Key Features Breakdown

### 1. Modular Code Structure

**Purpose**:  
To enhance maintainability, scalability, and readability by separating functionalities into distinct modules.

**Implementation**:

- **Module Separation**:
  - **`main_window.py`**: Orchestrates the application flow and integrates all components.
  - **`tree_view.py`**: Manages tree visualization and item interactions.
  - **`details_panel.py`**: Handles the UI for item details and comments.
  - **`command_builder.py`**: Builds the command string based on tree state.
  - **`data_manager.py`**: Handles data persistence.
  - **`tree_item.py`**: Defines the `TreeItem` class with additional attributes.
  - **`utils.py`**: Provides helper functions like `make_safe_filename`.

- **Benefits**:
  - **Maintainability**: Easier to manage and update individual modules.
  - **Collaboration**: Multiple developers can work on different modules simultaneously.
  - **Reusability**: Modules can be reused in other projects or extended independently.

### 2. JSON Data Management

**Purpose**:  
To persistently store individual directory trees with their annotations, filter states, and commands, enabling users to save and retrieve their work.

**Implementation**:

- **`DataManager` Class (`data_manager.py`)**:
  - Manages saving and loading of tree data to individual JSON files within a `trees` directory.
  - **Key Methods**:
    - `save_tree`: Saves a tree's data to a JSON file.
    - `load_trees_data`: Loads the list of saved trees.
    - `rename_tree`: Renames an existing tree file.
    - `delete_tree`: Deletes a tree file.

- **JSON Structure**:
  ```json
  {
    "title": "Project Tree",
    "path": "/path/to/directory",
    "root": {
      "name": "directory",
      "type": "directory",
      "comment": "",
      "filter_state": "none",
      "path": "/path/to/directory",
      "contents": [
        {
          "name": "src",
          "type": "directory",
          "comment": "",
          "filter_state": "filter",
          "path": "/path/to/directory/src",
          "contents": []
        },
        {
          "name": "README.md",
          "type": "file",
          "comment": "Project documentation",
          "filter_state": "none",
          "path": "/path/to/directory/README.md"
        }
      ]
    }
  }
  ```

**Interaction with Other Components**:  
The `DataManager` interacts with `MainWindow` for loading and saving operations, ensuring that the application state is preserved between sessions.

### 3. User Interface Components

**Purpose**:  
To provide an intuitive and organized interface for users to interact with the application.

**Implementation**:

- **Main Window (`main_window.py`)**:
  - **Layout Structure**:
    - **Top Section**: Load existing trees and load new directories.
    - **Title Editing**: Tree title input and editing controls.
    - **Content Area**: Split between the `TreeView` and `DetailsPanel`.
    - **Command Builder**: Displays the dynamically built `code2prompt` command.
    - **Bottom Section**: Status label and action buttons (Save, Close Tree).
  
- **Key Widgets**:
  - **`QComboBox`**: For selecting existing trees.
  - **`QLineEdit`**: For directory path input and tree title.
  - **`QTreeWidget`**: Displays the directory tree.
  - **`QTextEdit`**: For editing comments on selected items.
  - **`QLineEdit` (Read-only)**: Displays the command built by `CommandBuilder`.

**Interaction with Other Components**:  
The main window integrates all components, handling user actions and updating the interface accordingly.

### 4. Loading Directory Trees

**Purpose**:  
To visualize the structure of a selected directory in the `TreeView`, allowing users to navigate and interact with their filesystem.

**Implementation**:

- **`TreeView` Class (`tree_view.py`)**:
  - **`populate_tree` Method**:
    - Recursively adds directories and files to the tree.
    - Creates `TreeItem` instances with appropriate attributes.
  - **Path Handling**:
    - Stores full paths of items to build commands and manage states.

**Interaction with Other Components**:  
The `TreeView` communicates with `MainWindow` and `CommandBuilder` to update the UI and command string based on user interactions.

### 5. Adding and Editing Comments

**Purpose**:  
To allow users to annotate files and directories with comments for better documentation and understanding.

**Implementation**:

- **`DetailsPanel` Class (`details_panel.py`)**:
  - Displays the selected item's name and allows editing of its comment.
  - **Signals and Slots**:
    - Updates the item's `comment` attribute when the text changes.
    - Enables or disables the panel based on item selection.

**Interaction with Other Components**:  
The `DetailsPanel` updates the `TreeItem`'s comment, which is saved and loaded by the `DataManager`.

### 6. Command Builder Integration

**Purpose**:  
To dynamically build the `code2prompt` command based on the user's filter and exclude selections in the tree.

**Implementation**:

- **`CommandBuilder` Class (`command_builder.py`)**:
  - **`update_command` Method**:
    - Traverses the tree to collect paths of filtered and excluded items.
    - Builds the command string, prioritizing excludes over filters.
    - Updates the display in the read-only `QLineEdit`.

- **Filter and Exclude States**:
  - **Filter**: Include only these items.
  - **Exclude**: Exclude these items.
  - **States** are set via context menu options in the `TreeView`.

**Interaction with Other Components**:  
The `CommandBuilder` reacts to changes in the `TreeView` and updates the command accordingly.

### 7. Saving and Loading Trees

**Purpose**:  
To persistently store and retrieve annotated directory trees with their filter states and comments.

**Implementation**:

- **Saving Trees**:
  - **Process**:
    - User provides a title.
    - The tree structure is converted to JSON using `build_tree_json`.
    - The `DataManager` saves the JSON to a file named after the tree's title.

- **Loading Trees**:
  - **Process**:
    - User selects a saved tree from the dropdown.
    - The `DataManager` loads the JSON data.
    - The `TreeView` reconstructs the tree using `load_tree_from_json`.

**Interaction with Other Components**:  
Ensures that the user's work is preserved and can be resumed or modified later.

### 8. Error Handling and User Prompts

**Purpose**:  
To ensure a robust user experience by handling errors gracefully and providing informative prompts.

**Implementation**:

- **Unsaved Changes**:
  - Prompts the user when they attempt to load a new tree or exit with unsaved changes.

- **Invalid Inputs**:
  - Warns the user if an invalid directory is selected or if required fields are empty.

- **Duplicate Titles**:
  - Checks for existing tree titles to prevent overwriting unless confirmed.

- **Exceptions**:
  - Catches exceptions during file operations and displays error messages.

**Interaction with Other Components**:  
Maintains application stability and data integrity by preventing unintended actions.

### 9. Application Lifecycle Management

**Purpose**:  
To manage the application's startup, shutdown, and state transitions smoothly.

**Implementation**:

- **Initialization**:
  - Loads existing trees and initializes GUI components.

- **Closing Events**:
  - Overrides `closeEvent` to handle unsaved changes and confirm exit.

- **Clearing Data**:
  - Provides methods to clear the current tree data when loading new trees or closing.

**Interaction with Other Components**:  
Ensures that all components are correctly reset or preserved according to user actions.

---

## Workflow Example

### 1. Starting the Application

- **Action**:  
  - User launches the application by running `main.py`.

- **Process**:  
  - The `MainWindow` initializes.
  - The `DataManager` loads existing tree titles.
  - The GUI is set up with all components in place.

### 2. Loading a New Directory Tree

- **Action**:  
  - User clicks "Browse" to select a directory or enters a path manually.
  - The tree loads automatically upon selection.

- **Process**:  
  - `load_tree_from_path` in `MainWindow` calls `populate_tree` in `TreeView`.
  - The directory structure is displayed in the tree view.
  - The command builder updates to reflect the current directory.

### 3. Filtering and Excluding Items

- **Action**:  
  - User right-clicks on a tree item and selects "Filter Item" or "Exclude Item".

- **Process**:  
  - The item's `filter_state` is updated.
  - `update_item_appearance` changes the item's color.
  - `itemStateChanged` signal triggers an update to the command builder.

### 4. Adding Comments

- **Action**:  
  - User selects an item in the tree.
  - Edits the comment in the `DetailsPanel`.

- **Process**:  
  - The item's `comment` attribute is updated as the user types.
  - Changes are reflected immediately and marked as unsaved.

### 5. Building the Command

- **Action**:  
  - As the user filters or excludes items, the command builder updates.

- **Process**:  
  - `CommandBuilder` constructs the command based on the current tree state.
  - Displays the command in the read-only field for the user to copy or reference.

### 6. Saving the Tree

- **Action**:  
  - User provides a title and clicks "Save Tree".

- **Process**:  
  - The tree is serialized to JSON, including comments and filter states.
  - The `DataManager` saves the JSON to a file.
  - The tree title is added to the existing trees list.

### 7. Loading an Existing Tree

- **Action**:  
  - User selects a tree from the "Load Existing Tree" dropdown.

- **Process**:  
  - The `DataManager` loads the tree data.
  - `TreeView` reconstructs the tree with previous states and comments.
  - The command builder updates accordingly.

### 8. Closing the Application

- **Action**:  
  - User closes the application window.

- **Process**:  
  - If there are unsaved changes, the user is prompted to confirm exit.
  - The application closes gracefully, ensuring data integrity.

---

## Future Enhancements

1. **Executing Commands Directly**:
   - **Feature**: Allow users to execute the built `code2prompt` command directly from the GUI.
   - **Implementation**:
     - Integrate subprocess handling to run commands.
     - Provide output logs within the application.

2. **Comment Search and Filtering**:
   - **Feature**: Enable users to search for comments or filter items based on comments.
   - **Implementation**:
     - Add a search bar and implement filtering logic in `TreeView`.

3. **Tree Comparison Tool**:
   - **Feature**: Compare two saved trees to highlight differences.
   - **Implementation**:
     - Develop a comparison algorithm.
     - Visualize differences within the tree view.

4. **Customization Options**:
   - **Feature**: Allow users to customize the appearance (e.g., colors for filter states).
   - **Implementation**:
     - Add settings dialogs and persist preferences.

5. **Exporting Tree Structures**:
   - **Feature**: Export the tree structure and comments to formats like PDF or HTML.
   - **Implementation**:
     - Use report generation libraries to format and export data.

---

## Conclusion

**promptUI** offers a powerful and user-friendly interface for managing directory structures and integrating with the `code2prompt` tool. The modular design ensures that the application is maintainable and extensible. By allowing users to annotate, filter, and exclude items, it provides granular control over how directories are processed. The dynamic command builder bridges the gap between the GUI and command-line tools, enhancing productivity and efficiency.

As the application evolves, the focus remains on improving user experience and adding features that align with users' needs. The current architecture lays a solid foundation for future developments, ensuring that **promptUI** remains a valuable tool for project management and documentation.

---