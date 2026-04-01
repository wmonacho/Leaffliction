# Clean Architecture Quick Reference

## Running the Programs

### Part 1 - Dataset Analysis
```bash
python distribution.py leaves/images/
```

### Part 2 - Data Augmentation (Template Ready)
```bash
python augmentation.py leaves/images/ -o augmented_directory/
```

### Part 3 - Image Transformation
```bash
# Single image
python transformation.py path/to/image.jpg

# Entire directory
python transformation.py path/to/dataset/ -o output_dir/
```

### Part 4a - Train Classifier
```bash
python train.py leaves/images/ -t 0.2
# Model saved to: model.pkl
```

### Part 4b - Predict Disease
```bash
python predict.py path/to/test/image.jpg -m model.pkl
```

---

## Key Architectural Decisions

### **Dependency Inversion (DIP)**
```python
# ❌ BAD - depends on concrete implementation
repo = FileImageRepository()

# ✅ GOOD - depends on abstraction
repo: ImageRepository = FileImageRepository()
```

### **Strategy Pattern for Algorithms**
```python
# ✅ Easy to swap implementations
transformations = {
    "flip": FlipTransformation(),
    "rotate": RotateTransformation(),
}
service = ImageTransformationService(transformations)
```

### **Use Cases as Command Objects**
```python
# ✅ One use case = one user story
use_case = AnalyzeDatasetUseCase(repository)
analysis = use_case.execute(dataset_path)
```

### **Immutable Domain Entities**
```python
# ✅ Frozen dataclasses prevent accidental mutations
@dataclass(frozen=True)
class LeafImage:
    id: str
    array: np.ndarray  # Cannot be changed after creation
```

---

## Adding New Features (Part 2 - Data Augmentation)

The template is ready in `augmentation.py`. To implement:

```python
# 1. Create augmentation strategies in src/frameworks/
from src.application.services.image_transformation import ImageTransformationStrategy

class AugmentationStrategy(ImageTransformationStrategy):
    def apply(self, image: np.ndarray) -> np.ndarray:
        # Implement augmentation
        pass

# 2. Use in augmentation.py
augmentation_service = ImageTransformationService({
    "flip": FlipTransformation(),
    "rotate": RotateTransformation(),
    # ... all 6 augmentations
})

# 3. The rest is already wired via UseCase -> Controller -> Presenter
```

---

## SOLID Compliance Checklist

- ✅ **S**ingle Responsibility: Each class does one thing
- ✅ **O**pen/Closed: Open for extension (new transformations), closed for modification
- ✅ **L**iskov Substitution: All strategies are interchangeable
- ✅ **I**nterface Segregation: Abstract classes define minimal contracts
- ✅ **D**ependency Inversion: Depend on abstractions, inject implementations

---

## Idiomatic Python Features

| Feature | Usage |
|---------|-------|
| Type Hints | Full annotations for static analysis |
| Dataclasses | `@dataclass(frozen=True)` for immutability |
| ABC | Abstract base classes for contracts |
| Enums | Type-safe disease classification |
| Properties | Computed values with `@property` |
| f-strings | Modern string formatting |
| Pathlib | Cross-platform path handling |
| Strategy | Swappable algorithms |
| DI | Constructor injection of dependencies |

---

## File Organization

```
📁 src/
  📁 domain/              ← Business rules (no external deps)
  📁 application/         ← Use cases & services
  📁 adapters/            ← Controllers, repositories, presenters
  📁 frameworks/          ← External library wrappers
📁 distribution.py        ← Part 1 entry point
📁 augmentation.py        ← Part 2 entry point
📁 transformation.py      ← Part 3 entry point
📁 train.py              ← Part 4a entry point
📁 predict.py            ← Part 4b entry point
```

---

## Testing (Example)

```python
# tests/test_leaf_image.py
from src.domain.entities import LeafImage
from pathlib import Path

def test_leaf_image_creation():
    image = LeafImage(
        id="test",
        path=Path("test.jpg"),
        array=np.zeros((256, 256, 3)),
        label="Apple_healthy",
        plant_type="Apple"
    )
    assert image.get_shape() == (256, 256, 3)
    assert image.is_healthy() == True  # if added
```

---

## Next Steps

1. **Install dependencies**: `uv sync`
2. **Run Part 1**: `python distribution.py leaves/images/`
3. **Test Part 3**: `python transformation.py leaves/images/Apple_healthy/ -o test_output/`
4. **Train model**: `python train.py leaves/images/`
5. **Make predictions**: `python predict.py leaves/images/Apple_healthy/image.JPG -m model.pkl`
