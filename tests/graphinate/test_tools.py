from datetime import UTC, datetime

from graphinate.tools import VariableNameManager, utcnow


def test_utcnow():
    now = utcnow()
    assert isinstance(now, datetime)
    assert now.tzinfo == UTC


def test_variable_name_manager_basic():
    vnm = VariableNameManager(contract_underscores=True)
    assert vnm.make_valid('hello') == 'hello'
    assert vnm.make_valid('hello') == 'hello_1'
    assert vnm.make_valid('hello') == 'hello_2'


def test_variable_name_manager_empty_and_whitespace():
    assert VariableNameManager().make_valid('') == '_'
    assert VariableNameManager().make_valid('   ') == '_'
    assert VariableNameManager().make_valid(' \t\n ') == '_'



def test_variable_name_manager_digits_and_keywords():
    vnm = VariableNameManager()
    assert vnm.make_valid('123') == '_123'
    assert vnm.make_valid('for') == 'for_'
    assert vnm.make_valid('list') == 'list_'
    assert vnm.make_valid('class') == 'class_'


def test_variable_name_manager_special_chars_contracting():
    vnm = VariableNameManager(contract_underscores=True)
    assert vnm.make_valid('foo-bar@baz') == 'foo_bar_baz'
    assert vnm.make_valid('foo---bar') == 'foo_bar'


def test_variable_name_manager_special_chars_strict():
    vnm = VariableNameManager(contract_underscores=False)
    assert vnm.make_valid('foo-bar') == 'foo_bar'
    assert vnm.make_valid('a--b') == 'a__b'


def test_variable_name_manager_collision_and_histories():
    vnm = VariableNameManager()
    # Explicitly cause a collision where base_1 is candidate, but base_1 is already in inverse_history
    vnm.make_valid('foo_1')  # occupies 'foo_1'
    vnm.make_valid('foo')    # base 'foo', candidate 'foo'
    res = vnm.make_valid('foo')  # base 'foo', candidate 'foo_1' is taken, should become 'foo_2'
    assert res == 'foo_2'

    f_hist = vnm.forward_history
    assert 'foo' in f_hist
    assert 'foo_1' in f_hist

    inv_hist = vnm.inverse_history
    assert inv_hist['foo_1'] == 'foo_1'

    vnm.reset()
    assert len(vnm.forward_history) == 0
    assert len(vnm.inverse_history) == 0
