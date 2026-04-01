"""ARCHITECTURE.md - Clean Architecture Documentation

# Leaffliction Clean Architecture

## Overview

Leaffliction follows **Clean Architecture** principles with **SOLID** compliance:

```
┌─────────────────────────────────────────────────────────┐
│                   FRAMEWORKS & DRIVERS                   │
│            (distribution.py, train.py, etc.)            │
├─────────────────────────────────────────────────────────┤
│                    ADAPTERS LAYER                        │
│  Controllers  │  Repositories  │  Presenters            │
├─────────────────────────────────────────────────────────┤
│                 APPLICATION LAYER                        │
│    Use Cases (Business Rules) │ Services               │
├─────────────────────────────────────────────────────────┤
│                    DOMAIN LAYER                          │
│  Entities  │  Value Objects  │  Repositories (Abstract) │
└─────────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### 1. **Domain Layer** (`src/domain/`)
**Core business logic - no external dependencies**

- **Entities**: Immutable, frozen dataclasses representing core concepts
  - `LeafImage`: Leaf image with label and metadata
  - `Disease`: Disease types and properties
  - `ClassificationResult`: Prediction results

- **Value Objects**: Validated, immutable types
  - `ImagePath`: Ensures valid image paths

- **Repositories** (Abstract): Define contracts without implementation
  - `ImageRepository`: Abstract interface for image persistence

**Key Principle**: No dependencies on outer layers (Dependency Inversion)

---

### 2. **Application Layer** (`src/application/`)
**Business rules and orchestration - no UI/DB knowledge**

- **Use Cases**: One class per feature/command
  - `AnalyzeDatasetUseCase`: Part 1 - Dataset analysis
  - `TransformImagesUseCase`: Part 3 - Image transformation
  - `TrainClassifierUseCase`: Part 4 - Model training
  - `PredictDiseaseUseCase`: Part 4 - Prediction

- **Services**: Business logic helpers with abstractions
  - `ImageTransformationService`: Applies transformations (Strategy pattern)
  - `FeatureExtractionService`: Extracts features (Strategy pattern)
  - `ClassificationService`: Manages ML operations (Strategy pattern)

**Key Principles**: 
- Use cases are orchestrators (thin logic layer)
- Services encapsulate complex operations
- Dependency Injection in constructors

---

### 3. **Adapters Layer** (`src/adapters/`)
**Convert between external systems and domain**

- **Repositories** (Concrete): Implement abstract repositories
  - `FileImageRepository`: Load/save images from filesystem

- **Controllers**: CLI entry points (command handlers)
  - `DistributionController`: Part 1
  - `TransformationController`: Part 3
  - `TrainingController`: Part 4
  - `PredictionController`: Part 4

- **Presenters**: Format and display results
  - `AnalysisPresenter`: Display charts and statistics
  - `TransformationPresenter`: Show image transformations
  - `TrainingPresenter`: Training metrics
  - `PredictionPresenter`: Prediction with confidence

**Key Principles**:
- Controllers receive user input, delegate to use cases
- Presenters format domain objects for output
- No business logic in this layer

---

### 4. **Frameworks Layer** (`src/frameworks/`)
**External library integrations**

- **cv_transformations.py**: OpenCV-based image transformations
  - `FlipTransformation`, `RotateTransformation`, etc.
  - All implement `ImageTransformationStrategy`

- **cv_feature_extraction.py**: Feature extraction implementations
  - `HistogramFeatureExtractor`
  - `ColorMomentsFeatureExtractor`
  - `HybridFeatureExtractor`

- **sklearn_classification.py**: Machine learning with scikit-learn
  - `RandomForestClassification`: Implements `ClassificationStrategy`

**Key Principles**:
- Wrap external libraries in adapters
- Swap implementations without changing application logic
- Easy to test with mock implementations

---

## SOLID Principles Applied

### **S** - Single Responsibility
```python
# Each class has ONE reason to change
class AnalyzeDatasetUseCase:  # Only analyzes datasets
    pass

class AnalysisPresenter:  # Only presents analysis
    pass
```

### **O** - Open/Closed
```python
# Open for extension (new transformations)
class CustomTransformation(ImageTransformationStrategy):
    def apply(self, image): ...
    def get_name(self): ...

# Closed for modification (existing code unchanged)
service = ImageTransformationService({
    "custom": CustomTransformation()
})
```

### **L** - Liskov Substitution
```python
# All strategies are interchangeable
strategies: dict[str, ImageTransformationStrategy] = {
    "flip": FlipTransformation(),
    "rotate": RotateTransformation(),
    "custom": CustomTransformation(),  # Can swap in any implementation
}
```

### **I** - Interface Segregation
```python
# Abstract classes define minimal contracts
class ImageTransformationStrategy(ABC):
    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray: pass
    
    @abstractmethod
    def get_name(self) -> str: pass
```

### **D** - Dependency Inversion
```python
# Depend on abstractions, not concretions
class AnalyzeDatasetUseCase:
    def __init__(self, image_repository: ImageRepository):  # Abstract
        self._repository = image_repository  # Can inject any implementation
```

---

## Dependency Flow

```
Entry Points (distribution.py, train.py, etc.)
    ↓
Controllers (orchestrate flow)
    ↓
Use Cases (orchestrate business logic)
    ↓
Services (strategy patterns, complex logic)
    ↓
Domain (business entities)
    ↑
Adapters (repository implementations)
    ↓
Frameworks (external libraries: OpenCV, sklearn)
```

**No circular dependencies - everything flows inward!**

---

## Usage Examples

### Part 3 - Image Transformation
```bash
python transformation.py /path/to/image.jpg
python transformation.py /path/to/dataset/ -o /path/to/output/
```

### Part 4 - Training
```bash
python train.py /path/to/dataset/
```

### Part 4 - Prediction
```bash
python predict.py /path/to/test/image.jpg -m model.pkl
```

---

## Adding New Features (Maintaining Clean Architecture)

### Example: Add SVM Classifier

1. **Create framework implementation**:
```python
# src/frameworks/sklearn_svm.py
class SVMClassification(ClassificationStrategy):
    def train(self, features, labels, validation_split):
        # SVM implementation
        pass
    
    def predict(self, features):
        # SVM prediction
        pass
```

2. **Inject in script**:
```python
# train.py
classifier = SVMClassification()  # Swap RandomForest
classification_service = ClassificationService(classifier)
```

3. **No changes needed to**:
- Domain layer (entities stay same)
- Application layer (use cases stay same)
- Adapters layer (controllers/presenters stay same)

---

## Testing Strategy

### Unit Tests
```python
# Test domain entities (no dependencies)
def test_leaf_image_dimensions():
    image = LeafImage(id="test", path=Path("img.jpg"), ...)
    assert image.get_shape() == (256, 256, 3)

# Test use cases with mock dependencies
def test_analyze_dataset_empty():
    mock_repo = MockImageRepository([])
    use_case = AnalyzeDatasetUseCase(mock_repo)
    with pytest.raises(ValueError):
        use_case.execute(Path("/dataset"))
```

### Integration Tests
```python
# Test real repository + use case
def test_analyze_real_dataset(tmp_path):
    repo = FileImageRepository()
    use_case = AnalyzeDatasetUseCase(repo)
    result = use_case.execute(tmp_path)
    assert result.total_images > 0
```

---

## File Structure Summary

```
src/
├── domain/                    # Business rules
│   ├── entities/
│   │   ├── leaf_image.py
│   │   ├── disease.py
│   │   └── classification_result.py
│   ├── repositories/
│   │   └── image_repository.py  (abstract)
│   └── value_objects/
│       └── image_path.py
├── application/              # Use cases & services
│   ├── use_cases/
│   │   ├── analyze_dataset.py
│   │   ├── transform_images.py
│   │   ├── train_classifier.py
│   │   └── predict_disease.py
│   └── services/
│       ├── image_transformation.py
│       ├── feature_extraction.py
│       └── classification.py
├── adapters/                 # Controllers & I/O
│   ├── repositories/
│   │   └── file_image_repository.py
│   ├── controllers/
│   │   ├── distribution_controller.py
│   │   ├── transformation_controller.py
│   │   ├── training_controller.py
│   │   └── prediction_controller.py
│   └── presenters/
│       ├── analysis_presenter.py
│       ├── transformation_presenter.py
│       ├── training_presenter.py
│       └── prediction_presenter.py
└── frameworks/              # External libraries
    ├── cv_transformations.py
    ├── cv_feature_extraction.py
    └── sklearn_classification.py
```

---

## Idiomatic Python Features Used

✅ **Type Hints**: Full annotations for clarity
✅ **Dataclasses**: `@dataclass(frozen=True)` for immutability
✅ **ABC (Abstract Base Classes)**: Define contracts
✅ **Enums**: `DiseaseType` for type safety
✅ **Context Managers**: Safe resource handling
✅ **Properties**: `@property` for computed values
✅ **f-strings**: Modern string formatting
✅ **Pathlib**: Cross-platform path handling
✅ **Type validation**: `__post_init__` checks
✅ **Strategy Pattern**: Swappable algorithms
✅ **Dependency Injection**: Constructor injection
✅ **PEP 8 Compliance**: Flake8 compatible

---

## Next Steps

1. **Install dependencies**: `uv sync`
2. **Test Part 1**: `python distribution.py leaves/images/`
3. **Implement Part 3**: Already implemented - test with `python transformation.py`
4. **Implement Part 4**: Already implemented - test with `python train.py`
5. **Implement Part 2**: Data augmentation (template in `augmentation.py`)

"""
