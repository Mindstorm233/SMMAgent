# Advanced Complex Assembly Generation Guide

## Overview
The system now includes specialized prompts for generating complex 3D assemblies and components.

## Available Generators

### 1. Basic Generator (`blender_generator.py`)
- Simple 3D objects
- Basic shapes
- Quick prototypes

### 2. RAG Generator (`blender_generator_with_rag.py`)
- Enhanced with code templates
- Web search integration
- Better code quality

### 3. Advanced Assembly Generator (`advanced_assembly_generator.py`) ⭐ NEW
- Complex 3D assemblies
- Mechanical components
- Industrial designs
- Hierarchical structures
- Production-ready code

## Usage Examples

### Simple Assembly
```bash
python advanced_assembly_generator.py
# Input: "Create a gear assembly with 3 interlocking gears"
```

### Complex Mechanical System
```bash
python advanced_assembly_generator.py
# Input: "Design a robotic arm with base, 3 joint segments, gripper, mounting plate, and control housing"
```

### Industrial Component
```bash
python advanced_assembly_generator.py
# Input: "Create a pump assembly with motor housing, impeller, base plate, and mounting brackets"
```

## Key Features of Advanced Generator

### 1. Enhanced Prompt Engineering
- Modular architecture design
- Component hierarchy management
- Professional code standards
- Comprehensive error handling

### 2. Advanced 3D Operations
- Boolean operations
- Modifier stacks
- Parent-child relationships
- Collection organization
- Precision positioning

### 3. Material System
- Procedural materials
- UV mapping
- Texture coordinates
- Material libraries
- Rendering setup

### 4. Production Quality
- Error handling
- Logging
- Documentation
- Optimization
- Memory management

## Prompt Improvements

The new prompt includes:

1. **Architecture & Structure**
   - Modular functions
   - Reusable components
   - Proper organization
   - Clear naming

2. **Advanced Operations**
   - Boolean operations
   - Complex modifiers
   - Parametric design
   - Drivers and constraints

3. **Professional Standards**
   - Error handling
   - Documentation
   - Type hints
   - PEP 8 compliance

4. **Scene Management**
   - Collection organization
   - Object hierarchy
   - Scene optimization
   - Memory efficiency

## Best Practices

1. **Be Specific with Requirements**
   - Include dimensions
   - Specify materials
   - Describe relationships
   - Mention constraints

2. **Use Technical Terminology**
   - "interlocking gears" instead of "gears that fit together"
   - "mounting plate with bolt holes" instead of "base with holes"
   - "bearing housing" instead of "part that holds bearings"

3. **Describe Hierarchy**
   - Mention parent-child relationships
   - Specify assembly order
   - Indicate dependencies
   - Define component connections

4. **Include Technical Details**
   - Material specifications
   - Tolerance requirements
   - Motion constraints
   - Mounting methods

## Example Prompts

### Mechanical Assembly
```
"Create a gearbox assembly with input shaft, output shaft, 4 gears with different ratios, housing with mounting flanges, and oil seals"
```

### Structural Component
```
"Design a truss bridge section with diagonal supports, connection plates, bolt holes at joints, and load-bearing elements"
```

### Industrial Equipment
```
"Build a conveyor belt system with drive motor, rollers, frame, tensioning mechanism, and support stands"
```

### Precision Instrument
```
"Create a microscope assembly with optical tube, objective mount, stage mechanism, focus system, and base plate"
```

## Output Quality

The advanced generator produces code with:

- ✓ Modular, reusable functions
- ✓ Proper error handling
- ✓ Comprehensive comments
- ✓ Professional organization
- ✓ Optimized performance
- ✓ Production-ready quality

## Next Steps

1. Run the advanced generator with your complex assembly requirements
2. Review the generated code structure
3. Test in Blender
4. Customize parameters as needed
5. Iterate on prompt for refinement