import asyncpg
from asyncpg import Record
from typing import List



class Request:
    def __init__(self, connector):
        self.connector = connector


    async def check_table(self, name_table):
        query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = '{name_table}'
            );
        """
        return await self.connector.fetchval(query) 
    

    async def create_table(self, name_table):
        query = f"""
            CREATE TABLE {name_table} (
                user_id bigint NOT NULL,
                status text,
                description text,
                PRIMARY KEY (user_id)
            );  -- Remove the extra closing parenthesis here
        """
        await self.connector.execute(query)

        # Here, specify the correct table name ('name_table' variable) instead of 'users_for_sender'
        query = f"""
            INSERT INTO {name_table} (user_id, status, description) 
            SELECT user_id, 'waiting', '' FROM users WHERE status = 'member';
        """
        await self.connector.execute(query)


    async def delete_table(self, name_table):
        query = f"""
            DROP TABLE {name_table};
        """
        await self.connector.execute(query)
    


