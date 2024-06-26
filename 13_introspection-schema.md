# イントロスペクションスキーマ

<https://docs.graphene-python.org/projects/django/en/latest/introspection/>

- [イントロスペクションスキーマ](#イントロスペクションスキーマ)
  - [使用方法](#使用方法)
    - [GraphQL SDL表現](#graphql-sdl表現)
    - [高度な使用方法](#高度な使用方法)
    - [ヘルプ](#ヘルプ)

現代的なRelayは、GraphQLスキーマデータを提供することを要求する[Babel Relayプラグイン](https://facebook.github.io/relay/docs/en/installation-and-setup)を使用します。

Grapheneは、Babel Relayプラグインと互換性のあるスキーマデータを`schema.json`にダンプするDjango管理コマンドを備えています。

## 使用方法

プロジェクト設定内の`INSTALLED_APPS`に`graphene_django`を含めます。

```python
INSTALLED_APPS += ("graphene_django")
```

Grapheneスキーマが`tutorial.quickstart.schema`であると想定して、コマンドを実行します。

```sh
python manage.py graphql_schema --schema tutorial.quickstart.schema --out schema.json
```

コマンドは、プロジェクトルートディレクトリ内の`schema.json`に、完全なイントロスペクションスキーマをダンプします。
`babel-relay-plugin`にこのファイルを示すことで、Graphene GraphQL実装でRelayを使用する準備ができます。

そのスキーマファイルは、再現可能な正準表現を作成するために、並べ替えられています。

### GraphQL SDL表現

ファイルの拡張子を変更することで、GraphQLのSDLファイルをエクスポートすることもできます。

```sh
python manage.py graphql_schema --schema tutorial.quickstart.schema --out schema.graphql
```

`.graphql`ファイルとしてスキーマをエクスポートしたとき、`--indent`オプションは無視されます。

### 高度な使用方法

`--indent`オプションは、出力に使用されるインデントのスペースの数を指定するために使用できます。
デフォルトは`None`で、すべてのデータが1行で表示されます。

`--watch`オプションは、ウォッチモードで`python manage.py graphql_schema`を実行するために使用され、プロジェクトのファイルが変更されるたびに、新しいスキーマを自動的に出力します。

`python manage.py graphql_schema`コマンドを単純にするために、`settings.py`にパラメーターを指定できます。

```python
GRAPHENE = {
    "SCHEMA": "tutorial.quickstart.schema",
    "SCHEMA_OUTPUT": "data/schema.json",  # デフォルトはschema.json
    "SCHEMA_INDENT": 2,  # デフォルトはNoneで、すべてのデータを1行で表示
}
```

`python manage.py graphql_schema`の実行は、`<project root>/data/schema.json`にスキーマをダンプします。

### ヘルプ

コマンドの使用方法を確認するために、`python manage.py graphql_schema -h`を実行します。
