
tests = r"""
>>> from django.db import models
>>> from django.db.models.loading import cache

>>> from django_evolution.mutations import DeleteField
>>> from django_evolution.tests.utils import test_proj_sig, execute_test_sql
>>> from django_evolution.diff import Diff

>>> import copy
 
# All Fields
# db index (ignored for now)
# db tablespace (ignored for now)
# db column
# primary key
# unique

# M2M Fields
# to field
# db table

# Model Meta
# db table
# db tablespace (ignored for now)
# unique together (ignored for now)

# Now, a useful test model we can use for evaluating diffs
>>> class DeleteAnchor1(models.Model):
...     value = models.IntegerField()
>>> class DeleteAnchor2(models.Model):
...     value = models.IntegerField()
>>> class DeleteAnchor3(models.Model):
...     value = models.IntegerField()
>>> class DeleteAnchor4(models.Model):
...     value = models.IntegerField()

>>> class DeleteBaseModel(models.Model):
...     my_id = models.AutoField(primary_key=True)
...     char_field = models.CharField(max_length=20)
...     int_field = models.IntegerField()
...     int_field2 = models.IntegerField(db_column='non-default_db_column')
...     int_field3 = models.IntegerField(unique=True)
...     fk_field1 = models.ForeignKey(DeleteAnchor1)
...     m2m_field1 = models.ManyToManyField(DeleteAnchor3)
...     m2m_field2 = models.ManyToManyField(DeleteAnchor4, db_table='non-default_m2m_table')

>>> class CustomTableModel(models.Model):
...     value = models.IntegerField()
...     alt_value = models.CharField(max_length=20)
...     class Meta:
...         db_table = 'custom_table_name'

# Store the base signatures
>>> base_sig = test_proj_sig(DeleteBaseModel)
>>> custom_table_sig = test_proj_sig(CustomTableModel)

# Register the test models with the Django app cache
>>> cache.register_models('tests', CustomTableModel, DeleteBaseModel, DeleteAnchor1, DeleteAnchor2, DeleteAnchor3, DeleteAnchor4)

# Deleting a default named column
>>> class DefaultNamedColumnModel(models.Model):
...     my_id = models.AutoField(primary_key=True)
...     char_field = models.CharField(max_length=20)
...     int_field2 = models.IntegerField(db_column='non-default_db_column')
...     int_field3 = models.IntegerField(unique=True)
...     fk_field1 = models.ForeignKey(DeleteAnchor1)
...     m2m_field1 = models.ManyToManyField(DeleteAnchor3)
...     m2m_field2 = models.ManyToManyField(DeleteAnchor4, db_table='non-default_m2m_table')

>>> new_sig = test_proj_sig(DefaultNamedColumnModel)
>>> d = Diff(base_sig, new_sig)
>>> print [str(e) for e in d.evolution()['testapp']]
["DeleteField('TestModel', 'int_field')"]

>>> test_sig = copy.deepcopy(base_sig)
>>> test_sql = []
>>> for mutation in d.evolution()['testapp']:
...     test_sql.extend(mutation.mutate('testapp', test_sig))
...     mutation.simulate('testapp', test_sig)

>>> Diff(test_sig, new_sig).is_empty()
True

>>> execute_test_sql(test_sql)
ALTER TABLE "django_evolution_deletebasemodel" DROP COLUMN "int_field" CASCADE;

# Deleting a non-default named column
>>> class NonDefaultNamedColumnModel(models.Model):
...     my_id = models.AutoField(primary_key=True)
...     char_field = models.CharField(max_length=20)
...     int_field = models.IntegerField()
...     int_field3 = models.IntegerField(unique=True)
...     fk_field1 = models.ForeignKey(DeleteAnchor1)
...     m2m_field1 = models.ManyToManyField(DeleteAnchor3)
...     m2m_field2 = models.ManyToManyField(DeleteAnchor4, db_table='non-default_m2m_table')

>>> new_sig = test_proj_sig(NonDefaultNamedColumnModel)
>>> d = Diff(base_sig, new_sig)
>>> print [str(e) for e in d.evolution()['testapp']]
["DeleteField('TestModel', 'int_field2')"]

>>> test_sig = copy.deepcopy(base_sig)
>>> test_sql = []
>>> for mutation in d.evolution()['testapp']:
...     test_sql.extend(mutation.mutate('testapp', test_sig))
...     mutation.simulate('testapp', test_sig)

>>> Diff(test_sig, new_sig).is_empty()
True

>>> execute_test_sql(test_sql)
ALTER TABLE "django_evolution_deletebasemodel" DROP COLUMN "non-default_db_column" CASCADE;

# Deleting a column with database constraints (unique)
# TODO: Verify that the produced SQL is actually correct
# -- BK
>>> class ConstrainedColumnModel(models.Model):
...     my_id = models.AutoField(primary_key=True)
...     char_field = models.CharField(max_length=20)
...     int_field = models.IntegerField()
...     int_field2 = models.IntegerField(db_column='non-default_db_column')
...     fk_field1 = models.ForeignKey(DeleteAnchor1)
...     m2m_field1 = models.ManyToManyField(DeleteAnchor3)
...     m2m_field2 = models.ManyToManyField(DeleteAnchor4, db_table='non-default_m2m_table')

>>> new_sig = test_proj_sig(ConstrainedColumnModel)
>>> d = Diff(base_sig, new_sig)
>>> print [str(e) for e in d.evolution()['testapp']]
["DeleteField('TestModel', 'int_field3')"]

>>> test_sig = copy.deepcopy(base_sig)
>>> test_sql = []
>>> for mutation in d.evolution()['testapp']:
...     test_sql.extend(mutation.mutate('testapp', test_sig))
...     mutation.simulate('testapp', test_sig)

>>> Diff(test_sig, new_sig).is_empty()
True

>>> execute_test_sql(test_sql)
ALTER TABLE "django_evolution_deletebasemodel" DROP COLUMN "int_field3" CASCADE;

# Deleting a default m2m
>>> class DefaultM2MModel(models.Model):
...     my_id = models.AutoField(primary_key=True)
...     char_field = models.CharField(max_length=20)
...     int_field = models.IntegerField()
...     int_field2 = models.IntegerField(db_column='non-default_db_column')
...     int_field3 = models.IntegerField(unique=True)
...     fk_field1 = models.ForeignKey(DeleteAnchor1)
...     m2m_field2 = models.ManyToManyField(DeleteAnchor4, db_table='non-default_m2m_table')

>>> new_sig = test_proj_sig(DefaultM2MModel)
>>> d = Diff(base_sig, new_sig)
>>> print [str(e) for e in d.evolution()['testapp']]
["DeleteField('TestModel', 'm2m_field1')"]

>>> test_sig = copy.deepcopy(base_sig)
>>> test_sql = []
>>> for mutation in d.evolution()['testapp']:
...     test_sql.extend(mutation.mutate('testapp', test_sig))
...     mutation.simulate('testapp', test_sig)

>>> Diff(test_sig, new_sig).is_empty()
True

>>> execute_test_sql(test_sql)
DROP TABLE "django_evolution_deletebasemodel_m2m_field1";

# Deleting a m2m stored in a non-default table
>>> class NonDefaultM2MModel(models.Model):
...     my_id = models.AutoField(primary_key=True)
...     char_field = models.CharField(max_length=20)
...     int_field = models.IntegerField()
...     int_field2 = models.IntegerField(db_column='non-default_db_column')
...     int_field3 = models.IntegerField(unique=True)
...     fk_field1 = models.ForeignKey(DeleteAnchor1)
...     m2m_field1 = models.ManyToManyField(DeleteAnchor3)

>>> new_sig = test_proj_sig(NonDefaultM2MModel)
>>> d = Diff(base_sig, new_sig)
>>> print [str(e) for e in d.evolution()['testapp']]
["DeleteField('TestModel', 'm2m_field2')"]

>>> test_sig = copy.deepcopy(base_sig)
>>> test_sql = []
>>> for mutation in d.evolution()['testapp']:
...     test_sql.extend(mutation.mutate('testapp', test_sig))
...     mutation.simulate('testapp', test_sig)

>>> Diff(test_sig, new_sig).is_empty()
True

>>> execute_test_sql(test_sql)
DROP TABLE "non-default_m2m_table";

# Delete a foreign key
>>> class DeleteForeignKeyModel(models.Model):
...     my_id = models.AutoField(primary_key=True)
...     char_field = models.CharField(max_length=20)
...     int_field = models.IntegerField()
...     int_field2 = models.IntegerField(db_column='non-default_db_column')
...     int_field3 = models.IntegerField(unique=True)
...     m2m_field1 = models.ManyToManyField(DeleteAnchor3)
...     m2m_field2 = models.ManyToManyField(DeleteAnchor4, db_table='non-default_m2m_table')

>>> new_sig = test_proj_sig(DeleteForeignKeyModel)
>>> d = Diff(base_sig, new_sig)
>>> print [str(e) for e in d.evolution()['testapp']]
["DeleteField('TestModel', 'fk_field1')"]

>>> test_sig = copy.deepcopy(base_sig)
>>> test_sql = []
>>> for mutation in d.evolution()['testapp']:
...     test_sql.extend(mutation.mutate('testapp', test_sig))
...     mutation.simulate('testapp', test_sig)

>>> Diff(test_sig, new_sig).is_empty()
True

>>> execute_test_sql(test_sql)
ALTER TABLE "django_evolution_deletebasemodel" DROP COLUMN "fk_field1_id" CASCADE;

# Deleting a column from a non-default table
>>> class DeleteColumnCustomTableModel(models.Model):
...     alt_value = models.CharField(max_length=20)
...     class Meta:
...         db_table = 'custom_table_name'

>>> new_sig = test_proj_sig(DeleteColumnCustomTableModel)
>>> d = Diff(custom_table_sig, new_sig)
>>> print [str(e) for e in d.evolution()['testapp']]
["DeleteField('TestModel', 'value')"]

>>> test_sig = copy.deepcopy(custom_table_sig)
>>> test_sql = []
>>> for mutation in d.evolution()['testapp']:
...     test_sql.extend(mutation.mutate('testapp', test_sig))
...     mutation.simulate('testapp', test_sig)

>>> Diff(test_sig, new_sig).is_empty()
True

>>> execute_test_sql(test_sql)
ALTER TABLE "custom_table_name" DROP COLUMN "value" CASCADE;

"""