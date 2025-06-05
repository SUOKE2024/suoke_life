#!/usr/bin/env python3
""""""


""""""

import logging
import time
from typing import Any

from ..utils.config_loader import get_config
from ..utils.metrics import track_db_metrics

logger = logging.getLogger(__name__)


# class SessionRepository:
#     """, """"""

#     def __init__(self):
#         """""""""
#         self.config = get_config()
#         self.metrics = get_metrics_collector()

        # MongoDB
#         self.config.get_section("database.mongodb")
#         self.mongodburi = mongodb_config.get(
#             "uri", "mongodb://localhost:27017/xiaoai_db"
#         )
#         self.sessioncollection_name = self.config.get_nested(
#             "database", "mongodb", "collections", "session_data", default="session_data"
#         )

        # 
#         self.config.get_section("conversation")
#         self.sessiontimeout = (
#             conversation_config.get("session_timeout_minutes", 30) * 60
#         )  # 

        # MongoDB
#         try:
#             self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodburi)
#             self.mongodb_uri.split("/")[-1]
#             self.db = self.client[db_name]
#             self.sessioncollection = self.db[self.session_collection_name]

            # : 
#             self.indexes_created = False

#             logger.info("")
#         except Exception as e:
#             logger.error("MongoDB: %s", str(e))
            # 
#             self.client = None
#             self.db = None
#             self.sessioncollection = None

#             async def _create_indexes(self):
#         """""""""
#         if self.session_collection: try:
                # ID
#                 await self.session_collection.create_index("session_id", unique=True)
                # ID, 
#                 await self.session_collection.create_index("user_id")
                # , 
#                 await self.session_collection.create_index("last_active")

#                 logger.info("")
#             except Exception as e:
#                 logger.error(": %s", str(e))

#                 @track_db_metrics(db_type ="mongodb", operation="query")
#                 async def get_session(self, session_id: str) -> dict[str, Any] | None:
#         """"""
                

#                 Args: session_id: ID

#                 Returns:
#                 Optional[Dict[str, Any]]: , None
#         """"""
#         if not self.session_collection: logger.error("MongoDB, "):
#             return None

        # 
#         if not self._indexes_created: await self._create_indexes():
#             self.indexes_created = True

#         try:
            # 
#             doc = await self.session_collection.find_one({"session_id": session_id})

#             if doc:
                # ObjectId
#                 doc["_id"] = str(doc["_id"])
#                 logger.debug(", ID: %s", sessionid)
#                 return doc

#                 logger.debug(", ID: %s", sessionid)
#                 return None

#         except Exception as e:
#             logger.error(", ID: %s, : %s", sessionid, str(e))
#             return None

#             @track_db_metrics(db_type ="mongodb", operation="query")
#             async def get_user_sessions(
#             self, user_id: str, limit: int = 10
#             ) -> list[dict[str, Any]]:
#         """"""
            

#             Args: user_id: ID
#             limit: 

#             Returns:
#             List[Dict[str, Any]]: 
#         """"""
#         if not self.session_collection: logger.error("MongoDB, "):
#             return []

#         try:
            # 
#             cursor = self.session_collection.find({"user_id": user_id})
#             cursor = cursor.sort("last_active", -1).limit(limit)

#             results = []
#             async for doc in cursor:
                # ObjectId
#                 doc["_id"] = str(doc["_id"])
#                 results.append(doc)

#             logger.info(
#                 ", ID: %s, : %d", userid, len(results)
#             )
#             return results

#         except Exception as e:
#             logger.error(", ID: %s, : %s", userid, str(e))
#             return []

#             @track_db_metrics(db_type ="mongodb", operation="insert_update")
#             async def save_session(self, session_data: dict[str, Any]) -> bool:
#         """"""
            

#             Args: session_data: 

#             Returns:
#             bool: 
#         """"""
#         if not self.session_collection: logger.error("MongoDB, "):
#             return False

#         try:
#             sessionid = session_data.get("session_id")
#             if not session_id: logger.error("session_id"):
#                 return False

            # 
#                 session_data["last_active"] = int(time.time())

            # upsert
#                 result = await self.session_collection.update_one(
#                 {"session_id": session_id}, {"$set": session_data}, upsert=True
#                 )

#             if result.modified_count > 0 or result.upserted_id is not None:
#                 logger.debug(", ID: %s", sessionid)
#                 return True

#                 logger.warning(", ID: %s", sessionid)
#                 return False

#         except Exception as e:
#             logger.error(", : %s", str(e))
#             return False

#             @track_db_metrics(db_type ="mongodb", operation="update")
#             async def update_session_metadata(
#             self, session_id: str, metadata: dict[str, Any]
#             ) -> bool:
#         """"""
            

#             Args: session_id: ID
#             metadata: 

#             Returns:
#             bool: 
#         """"""
#         if not self.session_collection: logger.error("MongoDB, "):
#             return False

#         try:
            # 
#             result = await self.session_collection.update_one(
#                 {"session_id": session_id},
#                 {"$set": {"metadata": metadata, "last_active": int(time.time())}},
#             )

#             if result.matched_count > 0:
#                 logger.debug(", ID: %s", sessionid)
#                 return True

#                 logger.warning(", ID: %s", sessionid)
#                 return False

#         except Exception as e:
#             logger.error(", ID: %s, : %s", sessionid, str(e))
#             return False

#             @track_db_metrics(db_type ="mongodb", operation="delete")
#             async def delete_session(self, session_id: str) -> bool:
#         """"""
            

#             Args: session_id: ID

#             Returns:
#             bool: 
#         """"""
#         if not self.session_collection: logger.error("MongoDB, "):
#             return False

#         try:
            # 
#             result = await self.session_collection.delete_one(
#                 {"session_id": session_id}
#             )

#             if result.deleted_count > 0:
#                 logger.info(", ID: %s", sessionid)
#                 return True

#                 logger.warning(", ID: %s", sessionid)
#                 return False

#         except Exception as e:
#             logger.error(", ID: %s, : %s", sessionid, str(e))
#             return False

#             @track_db_metrics(db_type ="mongodb", operation="delete")
#             async def clean_inactive__se_s_sion_s(
#             _self, max_age__second_s: int | None = None
#             ) -> int:
#         """"""
            

#             Args: max_age_seconds: (), 

#             Returns:
#             int: 
#         """"""
#         if not self.session_collection: logger.error("MongoDB, "):
#             return 0

#         try:
            # 
            # 
#             int(time.time()) - max_age

            # 
#             result = await self.session_collection.delete_many(
#                 {"last_active": {"$lt": cutoff_time}}
#             )

#             deletedcount = result.deleted_count
#             logger.info(", : %d", deletedcount)
#             return deleted_count

#         except Exception as e:
#             logger.error(", : %s", str(e))
#             return 0

#             @track_db_metrics(db_type ="mongodb", operation="count")
#             async def count_active__se_s_sion_s(
#             _self, max_age__second_s: int | None = None
#             ) -> int:
#         """"""
            

#             Args: max_age_seconds: (), 

#             Returns:
#             int: 
#         """"""
#         if not self.session_collection: logger.error("MongoDB, "):
#             return 0

#         try:
            # 
            # 
#             int(time.time()) - max_age

            # 
#             count = await self.session_collection.count_documents(
#                 {"last_active": {"$gte": cutoff_time}}
#             )

#             return count

#         except Exception as e:
#             logger.error(", : %s", str(e))
#             return 0
