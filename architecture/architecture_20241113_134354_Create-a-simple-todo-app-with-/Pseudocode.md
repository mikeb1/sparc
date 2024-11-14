# Todo App with React

## Core Components

### App Component

```jsx
// App.js

import React, { useState } from 'react';
import TodoList from './TodoList';
import TodoForm from './TodoForm';

const App = () => {
  const [todos, setTodos] = useState([]); // State to hold the todo items

  // Function to add a new todo item
  const addTodo = (todo) => {
    setTodos([...todos, todo]); // Update the state with the new todo item
  };

  // Function to mark a todo item as completed
  const toggleTodo = (id) => {
    setTodos(
      todos.map((todo) => {
        if (todo.id === id) {
          return { ...todo, completed: !todo.completed }; // Toggle the completed status
        }
        return todo;
      })
    );
  };

  // Function to remove a todo item
  const removeTodo = (id) => {
    setTodos(todos.filter((todo) => todo.id !== id)); // Remove the todo item from the state
  };

  return (
    <div>
      <h1>Todo App</h1>
      <TodoForm addTodo={addTodo} /> {/* Render the TodoForm component */}
      <TodoList
        todos={todos}
        toggleTodo={toggleTodo}
        removeTodo={removeTodo}
      /> {/* Render the TodoList component */}
    </div>
  );
};

export default App;
```

### TodoList Component

```jsx
// TodoList.js

import React from 'react';
import TodoItem from './TodoItem';

const TodoList = ({ todos, toggleTodo, removeTodo }) => {
  return (
    <ul>
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          toggleTodo={toggleTodo}
          removeTodo={removeTodo}
        />
      ))}
    </ul>
  );
};

export default TodoList;
```

### TodoItem Component

```jsx
// TodoItem.js

import React from 'react';

const TodoItem = ({ todo, toggleTodo, removeTodo }) => {
  const { id, text, completed } = todo;

  const handleToggle = () => {
    toggleTodo(id); // Call the toggleTodo function with the todo id
  };

  const handleRemove = () => {
    removeTodo(id); // Call the removeTodo function with the todo id
  };

  return (
    <li>
      <input type="checkbox" checked={completed} onChange={handleToggle} />
      <span style={{ textDecoration: completed ? 'line-through' : 'none' }}>
        {text}
      </span>
      <button onClick={handleRemove}>Remove</button>
    </li>
  );
};

export default TodoItem;
```

### TodoForm Component

```jsx
// TodoForm.js

import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid'; // Library for generating unique ids

const TodoForm = ({ addTodo }) => {
  const [text, setText] = useState(''); // State to hold the input value

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      addTodo({ id: uuidv4(), text, completed: false }); // Create a new todo object and add it
      setText(''); // Clear the input field
    }
  };

  const handleChange = (e) => {
    setText(e.target.value); // Update the input value
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={handleChange}
        placeholder="Enter a new todo..."
      />
      <button type="submit">Add Todo</button>
    </form>
  );
};

export default TodoForm;
```

## Important Algorithms

### Array Methods

- `map`: Used to iterate over an array and create a new array with transformed elements.
- `filter`: Used to create a new array with elements that pass a certain condition.

### Object Destructuring

Destructuring is used to extract properties from objects and assign them to variables. This makes the code more concise and readable.

```js
const { id, text, completed } = todo;
```

### Spread Operator

The spread operator (`...`) is used to spread the elements of an array or properties of an object into a new array or object. This is useful for creating new arrays or objects based on existing ones.

```js
setTodos([...todos, todo]); // Add a new todo to the existing todos array
```

## Data Structures

### Todo Object

The todo items are represented as objects with the following properties:

```js
{
  id: string, // Unique identifier for the todo item
  text: string, // The text content of the todo item
  completed: boolean // Whether the todo item is completed or not
}
```

The `todos` state in the `App` component is an array of todo objects.

## Inline Comments

### App Component

```jsx
const App = () => {
  const [todos, setTodos] = useState([]); // State to hold the todo items

  // Function to add a new todo item
  const addTodo = (todo) => {
    setTodos([...todos, todo]); // Update the state with the new todo item
  };

  // Function to mark a todo item as completed
  const toggleTodo = (id) => {
    setTodos(
      todos.map((todo) => {
        if (todo.id === id) {
          return { ...todo, completed: !todo.completed }; // Toggle the completed status
        }
        return todo;
      })
    );
  };

  // Function to remove a todo item
  const removeTodo = (id) => {
    setTodos(todos.filter((todo) => todo.id !== id)); // Remove the todo item from the state
  };

  return (
    <div>
      <h1>Todo App</h1>
      <TodoForm addTodo={addTodo} /> {/* Render the TodoForm component */}
      <TodoList
        todos={todos}
        toggleTodo={toggleTodo}
        removeTodo={removeTodo}
      /> {/* Render the TodoList component */}
    </div>
  );
};
```

### TodoList Component

```jsx
const TodoList = ({ todos, toggleTodo, removeTodo }) => {
  return (
    <ul>
      {todos.map((todo) => (
        <TodoItem
          key={todo.id} // Unique key for each TodoItem
          todo={todo}
          toggleTodo={toggleTodo}
          removeTodo={removeTodo}
        />
      ))}
    </ul>
  );
};
```

### TodoItem Component

```jsx
const TodoItem = ({ todo, toggleTodo, removeTodo }) => {
  const { id, text, completed } = todo; // Destructure the todo object

  const handleToggle = () => {
    toggleTodo(id); // Call the toggleTodo function with the todo id
  };

  const handleRemove = () => {
    removeTodo(id); // Call the removeTodo function with the todo id
  };

  return (
    <li>
      <input type="checkbox" checked={completed} onChange={handleToggle} />
      <span style={{ textDecoration: completed ? 'line-through' : 'none' }}>
        {text}
      </span>
      <button onClick={handleRemove}>Remove</button>
    </li>
  );
};
```

### TodoForm Component

```jsx
const TodoForm = ({ addTodo }) => {
  const [text, setText] = useState(''); // State to hold the input value

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      addTodo({ id: uuidv4(), text, completed: false }); // Create a new todo object and add it
      setText(''); // Clear the input field
    }
  };

  const handleChange = (e) => {
    setText(e.target.value); // Update the input value
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={handleChange}
        placeholder="Enter a new todo..."
      />
      <button type="submit">Add Todo</button>
    </form>
  );
};
```

This pseudocode covers the core components, important algorithms, data structures, and inline comments for a simple Todo App built with React. It follows best practices and patterns specific to the React technology stack, such as using functional components, hooks for state management, and JSX syntax for rendering UI components.