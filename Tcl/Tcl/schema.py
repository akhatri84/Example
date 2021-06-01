import graphene
import graphql_jwt
from graphql import GraphQLError

import onboarding.schema
import supplychain.schema
import producer_manufacturer.schema
import material_composition.schema
import product.schema
import request_quote.schema
import get_support.schema
import product_files.schema
import supply_chain_files.schema
import app_user.schema
import brand_logo.schema
import profile_picture.schema
import api_config.schema
import shopify_store.schema
import favorite_product.schema
import wordpress_store.schema
import faq_module.schema
import impact_indicator.schema
import impact_indicator_files.schema
import productwtpsize.schema
import impactsize.schema
import dashboard.schema


class Query(dashboard.schema.Query,impactsize.schema.Query,productwtpsize.schema.Query,impact_indicator_files.schema.Query,impact_indicator.schema.Query,faq_module.schema.Query,favorite_product.schema.Query, api_config.schema.Query, profile_picture.schema.Query,
            brand_logo.schema.Query, app_user.schema.Query, supply_chain_files.schema.Query, product_files.schema.Query,
            get_support.schema.Query, request_quote.schema.Query, product.schema.Query, onboarding.schema.Query,
            supplychain.schema.Query, producer_manufacturer.schema.Query, material_composition.schema.Query,
            graphene.ObjectType):
    # this is root query class
    pass


class Mutation(impactsize.schema.Mutation,productwtpsize.schema.Mutation,impact_indicator_files.schema.Mutation,impact_indicator.schema.Mutation,faq_module.schema.Mutation,wordpress_store.schema.Mutation,favorite_product.schema.Mutation, shopify_store.schema.Mutation, api_config.schema.Mutation,
               profile_picture.schema.Mutation, brand_logo.schema.Mutation, app_user.schema.Mutation,
               supply_chain_files.schema.Mutation, product_files.schema.Mutation, get_support.schema.Mutation,
               request_quote.schema.Mutation, product.schema.Mutation, onboarding.schema.Mutation,
               supplychain.schema.Mutation, producer_manufacturer.schema.Mutation, material_composition.schema.Mutation,
               graphene.ObjectType):
    # this is root mutation class
    # consist mutations
    # token_auth gives JWT, if the credentials that we,
    # provide for given user are correct
    # if incorrect it should return an error and no token
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    # verify the token that we got from token auth
    verify_token = graphql_jwt.Verify.Field()
    # we are not going to use this in our app
    refresh_token = graphql_jwt.Refresh.Field()

# added Query and Mutation class to schema
schema = graphene.Schema(query=Query, mutation=Mutation)
