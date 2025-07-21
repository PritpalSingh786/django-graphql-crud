import graphene
import crudschema.schema as upload_schema

class Query(upload_schema.Query, graphene.ObjectType):
    pass

class Mutation(upload_schema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
