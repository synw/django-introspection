from typing import Dict
from .base import IntrospectionBaseTest
from unittest.mock import patch
from introspection import AppInspector, ModelRepresentation

from testapp.models import Market


class IntrospectionTestInspector(IntrospectionBaseTest):
    def test_inspector(self):
        with self.assertRaises(ModuleNotFoundError):
            AppInspector("unknown_app")
        app = AppInspector("testapp")
        self.assertEqual(app.name, "testapp")

    def test_model_representation_init(self):
        app = AppInspector("testapp")
        app.get_models()
        model = app.models[0]
        self.assertIsInstance(model, ModelRepresentation)
        self.assertEqual(type(model._model_type), type(Market))
        # from app and model names
        model = ModelRepresentation("testapp", model_name="Market")
        self.assertIsInstance(model, ModelRepresentation)
        self.assertEqual(type(model._model_type), type(Market))
        with self.assertRaises(ValueError):
            ModelRepresentation()

    def test_model_representation_methods(self):
        model = ModelRepresentation("testapp", model_name="Market")
        Market.objects.create(name="Binance")
        self.assertEqual(model.count(), 1)
        with self.assertRaises(LookupError):
            model._get("unknown_app", "unknown_model")
        with self.assertRaises(LookupError):
            model._get("testapp", "unknown_model")

    @patch("builtins.print")
    def test_titles(self, mock_print):
        model = ModelRepresentation("testapp", model_name="Market")
        info = model.fields_info()
        print(info)

    def test_model_field_representation(self):
        model = ModelRepresentation("testapp", model_name="Trade")
        d: Dict[str, str] = {"name": "id", "class": "BigAutoField", "related_name": ""}
        self.assertDictEqual(model.fields["id"].to_dict(), d)
