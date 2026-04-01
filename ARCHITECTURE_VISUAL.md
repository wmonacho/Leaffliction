# 🏗️ Clean Architecture Visual Guide

## The Onion Architecture Layers

```
                    ╔════════════════════════════════════╗
                    ║   Frameworks & Drivers Layer       ║
                    ║                                    ║
                    ║  distribution.py  train.py         ║
                    ║  transformation.py  predict.py     ║
                    ╚═════════════╤══════════════════════╝
                                  │ imports from
                    ╔═════════════▼══════════════════════╗
                    ║   Adapters Layer                   ║
                    ║                                    ║
                    ║  ┌─ Controllers (CLI handlers)    ║
                    ║  ├─ Repositories (I/O)            ║
                    ║  └─ Presenters (Output)           ║
                    ╚═════════════╤══════════════════════╝
                                  │ imports from
                    ╔═════════════▼══════════════════════╗
                    ║  Application Layer                 ║
                    ║                                    ║
                    ║  ┌─ Use Cases (business rules)    ║
                    ║  └─ Services (strategies)         ║
                    ╚═════════════╤══════════════════════╝
                                  │ imports from
                    ╔═════════════▼══════════════════════╗
                    ║   Domain Layer (Core Business)     ║
                    ║                                    ║
                    ║  ┌─ Entities (data holders)       ║
                    ║  ├─ Value Objects (validated)     ║
                    ║  └─ Repositories (contracts)      ║
                    ║                                    ║
                    ║  🎯 ZERO external dependencies   ║
                    ╚════════════════════════════════════╝
```

---

## Module Dependency Chart

```
ENTRY POINTS (Scripts)
    │
    ├─→ distribution.py ──→ DistributionController
    ├─→ transformation.py ──→ TransformationController
    ├─→ train.py ──→ TrainingController
    └─→ predict.py ──→ PredictionController
            │
            └─→ USE CASES
                    │
                    ├─→ AnalyzeDatasetUseCase
                    ├─→ TransformImagesUseCase
                    ├─→ TrainClassifierUseCase
                    └─→ PredictDiseaseUseCase
                            │
                            ├─→ SERVICES
                            │   ├─→ ImageTransformationService
                            │   ├─→ FeatureExtractionService
                            │   └─→ ClassificationService
                            │
                            ├─→ REPOSITORIES (Abstract)
                            │   └─→ ImageRepository
                            │
                            └─→ DOMAIN ENTITIES
                                ├─→ LeafImage
                                ├─→ Disease
                                ├─→ ClassificationResult
                                ├─→ ImagePath
                                └─→ DiseaseType

CONCRETE IMPLEMENTATIONS
    ├─→ FileImageRepository (adapters/)
    ├─→ FlipTransformation (frameworks/)
    ├─→ RotateTransformation (frameworks/)
    ├─→ HistogramFeatureExtractor (frameworks/)
    ├─→ RandomForestClassification (frameworks/)
    └─→ Presenters (adapters/)
```

---

## Data Flow: Part 3 (Transformation)

```
User Command
    ↓
transformation.py
    │ ┌─────────────────────────────┐
    ├→ Create Dependencies:         │
    │  • FileImageRepository        │
    │  • ImageTransformationService │
    │  • TransformationPresenter    │
    │ └─────────────────────────────┘
    ↓
TransformationController.handle_single_image()
    ↓
TransformImagesUseCase.execute_single_image()
    │ ┌────────────────────────────────────┐
    ├→ Load image via:                     │
    │  ImageRepository.load_from_path()    │
    │ └────────────────────────────────────┘
    │ ┌────────────────────────────────────┐
    ├→ Transform via:                      │
    │  ImageTransformationService          │
    │  .apply_all_transformations()        │
    │ └────────────────────────────────────┘
    ↓
TransformationOutput
    {
      original: np.ndarray,
      transformations: {
        "flip": ...,
        "rotate": ...,
        "skew": ...,
        "shear": ...,
        "crop": ...,
        "distortion": ...
      },
      histogram: np.ndarray
    }
    ↓
TransformationPresenter.present_single()
    ↓
Display using Matplotlib
```

---

## Data Flow: Part 4a (Training)

```
User Command: python train.py leaves/images/
    ↓
train.py
    │ ┌──────────────────────────────┐
    ├→ Create Dependencies:           │
    │  • FileImageRepository         │
    │  • HistogramFeatureExtractor   │
    │  • RandomForestClassification  │
    │  • Services & Controllers      │
    │ └──────────────────────────────┘
    ↓
TrainingController.handle()
    ↓
TrainClassifierUseCase.execute()
    │ ┌──────────────────────────────┐
    ├→ Load all images:              │
    │  ImageRepository               │
    │  .load_from_directory()        │
    │ └──────────────────────────────┘
    │ ┌──────────────────────────────┐
    ├→ Extract features:             │
    │  FeatureExtractionService      │
    │  .extract() for each image     │
    │ └──────────────────────────────┘
    │ ┌──────────────────────────────┐
    ├→ Train with validation:        │
    │  ClassificationService         │
    │  .train_with_validation()      │
    │ └──────────────────────────────┘
    ↓
TrainingResult
    {
      training_size: int,
      validation_size: int,
      validation_accuracy: float,
      num_classes: int,
      class_names: list[str]
    }
    ↓
TrainingPresenter.present()
    ↓
Display metrics (console + charts)
    ↓
Save model.pkl
```

---

## Data Flow: Part 4b (Prediction)

```
User Command: python predict.py image.jpg -m model.pkl
    ↓
predict.py
    │ ┌──────────────────────────────┐
    ├→ Create Dependencies:           │
    │  • FileImageRepository         │
    │  • HistogramFeatureExtractor   │
    │  • RandomForestClassification  │
    │  (loaded from disk)            │
    │ └──────────────────────────────┘
    ↓
PredictionController.handle()
    ↓
PredictDiseaseUseCase.execute()
    │ ┌──────────────────────────────┐
    ├→ Load image:                   │
    │  ImageRepository               │
    │  .load_from_path()             │
    │ └──────────────────────────────┘
    │ ┌──────────────────────────────┐
    ├→ Extract features:             │
    │  FeatureExtractionService      │
    │  .extract()                    │
    │ └──────────────────────────────┘
    │ ┌──────────────────────────────┐
    ├→ Make prediction:              │
    │  ClassificationService         │
    │  .predict()                    │
    │ └──────────────────────────────┘
    ↓
ClassificationResult
    {
      predicted_disease: str,
      confidence: float,
      original_image: np.ndarray,
      transformed_image: np.ndarray
    }
    ↓
PredictionPresenter.present()
    ↓
Display images + disease + confidence
```

---

## SOLID Principles in Action

### S - Single Responsibility

```
❌ BAD: One class does everything
class LeafAnalyzer:
    def load_image(self): ...
    def analyze_dataset(self): ...
    def display_charts(self): ...
    def train_model(self): ...

✅ GOOD: Each class has ONE job
class AnalyzeDatasetUseCase:
    def execute(self): ...  # Only analyzes

class AnalysisPresenter:
    def present(self): ...  # Only displays

class FileImageRepository:
    def load_from_directory(self): ...  # Only loads
```

### O - Open/Closed

```
✅ OPEN for extension (add new transformations without touching existing code)
strategies = {
    "flip": FlipTransformation(),
    "rotate": RotateTransformation(),
    "my_custom": CustomTransformation(),  # ← Add new without modifying service
}
service = ImageTransformationService(strategies)

✅ CLOSED for modification (existing strategies unchanged)
```

### L - Liskov Substitution

```
✅ All strategies are interchangeable
def apply_transformations(
    transformations: dict[str, ImageTransformationStrategy]
):
    for strategy in transformations.values():
        strategy.apply(image)  # Works with ANY implementation

# Can substitute any of these without changing code:
class FlipTransformation(ImageTransformationStrategy): ...
class RotateTransformation(ImageTransformationStrategy): ...
class MyCustomTransformation(ImageTransformationStrategy): ...
```

### I - Interface Segregation

```
✅ Abstract classes define MINIMAL contracts
class ImageRepository(ABC):
    @abstractmethod
    def load_from_path(self, path: Path) -> LeafImage: pass
    
    @abstractmethod
    def load_from_directory(self, dir: Path) -> list[LeafImage]: pass

# Clients depend only on what they need
use_case = AnalyzeDatasetUseCase(repository)  # Use contracts
```

### D - Dependency Inversion

```
❌ BAD: Depend on concrete classes
repo = FileImageRepository()  # Tightly coupled

✅ GOOD: Depend on abstractions
repo: ImageRepository = FileImageRepository()  # Can swap anytime
```

---

## Test Pyramid

```
        ┌─────────────────────┐
        │   E2E Tests (1-2)   │
        │  (Full workflows)   │
        └─────────────────────┘
             ▲
             │
        ┌───────────────────┐
        │ Integration (5-10)│
        │ (Real components) │
        └───────────────────┘
             ▲
             │
        ┌───────────────────────┐
        │  Unit (30-50)         │
        │  (Pure functions)     │
        │  (Mocked deps)        │
        └───────────────────────┘
```

**Why this works**:
- Unit tests are fast (pure logic)
- Integration tests validate contracts
- E2E tests verify real workflows

---

## Feature Addition Checklist

Adding a new transformation (e.g., Gaussian Blur):

```
Domain Layer:
  ☐ Define new entity/value object if needed
  
Application Layer:
  ☐ Update use cases if new business logic
  
Adapters Layer:
  ☐ Update controllers if new CLI commands
  ☐ Update presenters if new output format
  
Frameworks Layer:
  ✅ Create BlurTransformation(ImageTransformationStrategy)
  ✅ Register in transformation service
  
Entry Points:
  ✅ Add to script if needed
```

---

## Clean Architecture Checklist

Your implementation includes:

- ✅ **Domain Layer**: Pure business logic, no framework dependencies
- ✅ **Application Layer**: Use cases as orchestrators, services for logic
- ✅ **Adapters Layer**: Controllers, repositories, presenters
- ✅ **Frameworks Layer**: External library wrappers
- ✅ **Dependency Injection**: Constructor injection throughout
- ✅ **Strategy Pattern**: Swappable algorithms
- ✅ **Repository Pattern**: Abstract persistence
- ✅ **Type Hints**: Full annotations
- ✅ **Immutable Entities**: Frozen dataclasses
- ✅ **Error Handling**: Proper validation
- ✅ **SOLID Principles**: Applied consistently

---

## Performance Considerations

```
Part 3 (Transformation):
  Single image: ~50-100ms (6 transformations)
  Directory (100 images): ~5-10s

Part 4a (Training):
  Small dataset (1000 images): ~1-2s
  Large dataset (10000+ images): ~10-30s

Part 4b (Prediction):
  Single image: ~10-20ms
```

---

**Your architecture is ready for production! 🎉**
