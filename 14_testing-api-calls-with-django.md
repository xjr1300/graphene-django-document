# DjangoでAPI呼び出しをテストする

<https://docs.graphene-python.org/projects/django/en/latest/testing/>

- [DjangoでAPI呼び出しをテストする](#djangoでapi呼び出しをテストする)
  - [ユニットテストを使用する](#ユニットテストを使用する)
  - [pytestを使用する](#pytestを使用する)

## ユニットテストを使用する

API呼び出しをユニットテストしたい場合、*GraphQLTestCase*クラスからテストケースを派生してください。

エンドポイントは、*GraphQLTestCase`の`GRAPHQL_URL`属性を介して設定されます。
デフォルトのエンドポイントは、`GRAPHQL_URL = "/graphql/"`です。

使用方法は次のとおりです。

```python
import json

from graphene_django.utils.testing import GraphQLTestCase


class MyFancyTestCase(GraphQLTestCase):
    def test_some_query(self):
        response = self.query(
            """
            query {
              myModel {
                id
                name
              }
            }
            """,
            op_name="myModel"
        )

        content = json.loads(response.content)

        # エラーを得た場合、これはステータスコードを検証します。
        self.assertResponseNoErrors(response)

        # 好みのアサートを追加します。
        ...

    def test_query_with_variables(self):
        response = self.query(
            """
            query myModel($id: Int!) {
              myModel(id: $id) {
                id
                name
              }
            }
            """.
            op_name="myModel",
            variables={"id": 1}
        )

        content = json.loads(response.content)

        self.assertResponseNoErrors(response)

        ...

    def test_some_mutation(self):
        response = self.query(
            """
            mutation myMutation($input: MyMutationInput!) {
              myMutation(input: $input) {
                myModel {
                  id
                  name
                }
              }
            }
            """,
            op_name="myMutation",
            input_data={"my_field": "foo", "other_field": "bar"}
        )

        self.assertResponseNoErrors(response)

        ...
```

## pytestを使用する

pytestを使用するために、次のクエリヘルパーを使用して簡単なフィクスチャーを定義してください。

```python
# graphql_queryヘルパーを使用してフィクスチャーと、`pytest-django`の`client`を作成してください。
import json

import pytest
from graphene_django.utils.testing import graphql_query


@pytest.fixture
def client_query(client):
    def func(*args, **kwargs):
        return graphql_query(*args, **kwargs, client=client)

    return func


# client_queryフィクスチャーを使用してクエリをテストします。
def test_some_query(client_query):
    response = client_query(
        """
        query {
          myModel {
            id
            name
          }
        }
        """,
        op_name="myModel"
    )

    content = json.loads(response.content)

    assert "errors" not in content
```
