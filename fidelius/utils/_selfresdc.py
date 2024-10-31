__all__ = [
    'SelfResolvingFromDictDataclass',
]
from ccptools.structs import *
from ccptools import dtu
from ccptools.tpu import strimp
import dataclasses
from typing import _GenericAlias, _SpecialForm  # noqa

_T_ANNOTATION = Union[str, type, _GenericAlias, _SpecialForm, ForwardRef]


def _get_annotation_type(annotation: _T_ANNOTATION, globalns=None, localns=None) -> Type:
    # TODO(thordurm@ccpgames.com>) 2024-05-16: Lists/Sets/Dics of Classes?!?
    if isinstance(annotation, _SpecialForm) and annotation is Any:
        return Any

    if isinstance(annotation, _GenericAlias):
        if annotation.__origin__ is Union:
            real_annotations = [a for a in annotation.__args__ if a is not None.__class__]  # noqa
            if len(real_annotations) == 1:
                annotation = real_annotations[0]
            else:
                raise TypeError(f'cant get type for multiple annotations: {real_annotations}')
        elif isinstance(annotation.__origin__, type):
            annotation = annotation.__origin__

        return _get_annotation_type(annotation, globalns=globalns, localns=localns)

    if isinstance(annotation, str):
        # TODO(thordurm@ccpgames.com>) 2024-05-16: Check globals/locals?!?
        if '.' in annotation:
            return strimp.get_class(annotation, reraise=True)
        else:
            annotation = ForwardRef(annotation)

    if isinstance(annotation, ForwardRef):
        annotation = annotation._evaluate(globalns, localns)  # noqa

    if isinstance(annotation, type):
        return annotation

    raise TypeError(f'cant find type of annotation: {annotation}')


@dataclasses.dataclass
class SelfResolvingFromDictDataclass:
    extra_attr: dataclasses.InitVar[Optional[Dict[str, Any]]] = None
    _extra_attr: Dict[str, Any] = dataclasses.field(default_factory=dict, init=False)

    def __post_init__(self, extra_attr: Dict[str, Any] = None):
        if extra_attr:
            self._extra_attr = extra_attr

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'SelfResolvingFromDictDataclass':
        fd = {f.name: f for f in dataclasses.fields(cls)}
        kwargs = {}
        extras = {}
        for k, v in d.items():
            if k in fd:  # Field is in class
                if v is None:
                    kwargs[k] = v
                    continue

                field = fd.get(k)
                field_type = None
                if field.type:
                    field_type = _get_annotation_type(field.type, globalns=globals(), localns=locals())

                if not field_type or field_type is Any:  # No type annotation!
                    kwargs[k] = v
                    continue

                if isinstance(v, field_type):  # Types are the same!
                    kwargs[k] = v
                    continue

                if field_type is Datetime:
                    kwargs[k] = dtu.any_to_datetime(v)
                    continue

                if field_type is Time:
                    kwargs[k] = dtu.any_to_datetime(v).time()
                    continue

                if field_type is Date:
                    kwargs[k] = dtu.any_to_datetime(v).date()
                    continue

                if isinstance(v, dict):
                    if dataclasses.is_dataclass(field_type):
                        if hasattr(field_type, 'from_dict'):
                            kwargs[k] = field_type.from_dict(v)
                        else:
                            kwargs[k] = field_type(**v)
                    else:
                        kwargs[k] = field_type(**v)
                    continue

                raise ValueError(f'No idea how to handle this: {k=}, {v=}, {field_type=}')

            else:
                extras[k] = v

        return cls(**kwargs, extra_attr=extras)  # noqa

    def __getattr__(self, item):
        if item in self._extra_attr:
            return self._extra_attr[item]
        return EmptyDict

    def __setattr__(self, key, value):
        if key in {f.name for f in dataclasses.fields(self)}:
            super().__setattr__(key, value)
        else:
            self._extra_attr[key] = value
