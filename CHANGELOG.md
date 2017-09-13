
### 1.0.73 (2017-09-06)

#### Feature 
* **es_recommend_optimize**
  *  Fix code check issue ([32fa0cf4](https://github.com/aml-development/ozp-backend/commit/32fa0cf4d25bc01f12ef573406ebe2cf2803ba78))
  *  Combined code into one file for maintainability ([e3374160](https://github.com/aml-development/ozp-backend/commit/e337416094838e81cfc5deac47f1c7736b91052e))
  *  Fixed code execution issues ([da38458f](https://github.com/aml-development/ozp-backend/commit/da38458fae4ea5b333d0be8c58e91f709ee34786))
  *  Fix partial Travis issues. ([b5a739fc](https://github.com/aml-development/ozp-backend/commit/b5a739fcbbf7a1ae3f6933ed17270c2fa18414c7))
  *  Port changes from PR #344 ([52e9bc01](https://github.com/aml-development/ozp-backend/commit/52e9bc010f2a1d920a27dc298b25b2ace8a19584))       

#### Merge Pull Requests  
* Merge pull request #335 from aml-development/refactor_data ([d6cab253](https://github.com/aml-development/ozp-backend/commit/d6cab25339e01f6bd6407efc9f8a623c0cb90123))           

### 1.0.72 (2017-08-28)

#### Feature 
* **titlepriority**
  *  Removed print statement that is not needed. ([89c10296](https://github.com/aml-development/ozp-backend/commit/89c10296ab4e08b056f7896d8d7a2ea2df861dde))
  *  Change to make title preferred over other values ([e465b0d7](https://github.com/aml-development/ozp-backend/commit/e465b0d7bce224d84966bdc8b9aa5b219f708a8a))     

#### Fixes  
* **recommend**:  Fixed recommend.py ([99334154](https://github.com/aml-development/ozp-backend/commit/993341547ab887467789c4d769a3ec20ccb39cd1))    

#### Refactor 
* **sample_data**
  *  Refactor Elasticsearch Client code ([dee09ef7](https://github.com/aml-development/ozp-backend/commit/dee09ef7fcc3a5d159fdb9e2fd55b7b4ba579817))
  *  Finished fixing unit test ([a88fc438](https://github.com/aml-development/ozp-backend/commit/a88fc43890e569c998bf4b82ecd0e4f5ff824852))
  *  Refactoring Unit Test ([b1836ff7](https://github.com/aml-development/ozp-backend/commit/b1836ff790d0c492e97239dc9f879df674d5b285))
  *  Fixed Unit Test ([8fabb2a5](https://github.com/aml-development/ozp-backend/commit/8fabb2a59d037326f4c6d31131c9784f8aeda7d8))
  *  Ordered Listing Data ([3857805c](https://github.com/aml-development/ozp-backend/commit/3857805c4c052c877850519fb065aa34fe37ddd7))     
* **travis-ci**:  Add Elasticsearch to TravisCI for integration test ([7c585aa0](https://github.com/aml-development/ozp-backend/commit/7c585aa0599daa3c4df3d868a5bc7aca2356d85a))    

#### Merge Pull Requests  
* Merge branch 'master' into refactor_data ([7ebb54f5](https://github.com/aml-development/ozp-backend/commit/7ebb54f5ab82dd2c08267581247f0fa54743d5c0))         

#### Changes  
* updating the peer object serialization so it is not serialized into a string instead of being kept as an object (#342) ([68013279](https://github.com/aml-development/ozp-backend/commit/68013279176cdb40441ced674e83d12a22e90aef))     

### 1.0.71 (2017-08-16)

#### Feature  
* **recommend_optimize**:  Added comments and reduced the weighting of content based results. ([af6b618e](https://github.com/aml-development/ozp-backend/commit/af6b618e032147c41d074f02b07acabebf7c9f16))    
* **recommender_optimize**:  Initial baseline changes to have all recommendation engines operate on same rating system.  Also corrected issue found during a obscure test for content based. ([2edc3d40](https://github.com/aml-development/ozp-backend/commit/2edc3d40225327ed9178ccae05deed915e53b9e4))    
* **notification**:  Change when notifications send for listing changes ([f47449fa](https://github.com/aml-development/ozp-backend/commit/f47449fab72ad231e092bf97cc95564b69525308))     

#### Refactor 
* **sample_data**
  *  Updated  listings.yaml and added images ([ec064b03](https://github.com/aml-development/ozp-backend/commit/ec064b036a13ba4a22514c0a26c694f99b8288ec))
  *  More listings to listings.yaml and images ([a6775326](https://github.com/aml-development/ozp-backend/commit/a677532638ed21151c02d97bc2874fffd45b156e))
  *  Added more listings to listings.yaml and images ([08f9e83c](https://github.com/aml-development/ozp-backend/commit/08f9e83ccaf9ed5f36143079a51a7351422e0216))
  *  Added Updated Listings,Categories,Contacts YAMLs ([55d829fc](https://github.com/aml-development/ozp-backend/commit/55d829fc4b6e15603c79a69de224a3155fbc6f2d))     

#### Merge Pull Requests  
* Merge pull request #339 from aml-development/recommend_optimize ([8ce547c4](https://github.com/aml-development/ozp-backend/commit/8ce547c45210f5c817150045cdaaaeb77fd428c9))
* Merge pull request #338 from aml-development/revised_notification ([f15bb334](https://github.com/aml-development/ozp-backend/commit/f15bb33430a78be689310eaa4f3e75446e10be23))           

### 1.0.70 (2017-08-09)

#### Feature  
* **recommender_optimize**:  Initial working with adjusting weights using a normalizing function. ([9729d75e](https://github.com/aml-development/ozp-backend/commit/9729d75ec95a0a0fecc56317b6d3dfb6227912ed))   
* **es_recommend_content**
  *  removed unused code and fixed comment ([3e895282](https://github.com/aml-development/ozp-backend/commit/3e895282c9518d9df35579d7bad901aff9265543))
  *  Added code to pull text for each listing in a profile, fix new user problem with a solution, added code to perform searches adquately and added a few TODO's that are not necessary for initial deployment and may change if live requests are requested. ([8b1c746d](https://github.com/aml-development/ozp-backend/commit/8b1c746d392eb8e11f6bb30fe43ae9ab50b1f221))     
* **exporter**:  Added Listing Exporter ([54fb20ee](https://github.com/aml-development/ozp-backend/commit/54fb20ee0ed0fd98d416c4fe70afaddf51bf557e))    

#### Fixes  
* Fixed Typo ([7295ef77](https://github.com/aml-development/ozp-backend/commit/7295ef7792f10ed1508d75b695169e47eb89ce80))    

#### Refactor 
* **sample_data**
  *  Format Map for launch_url field ([f66e1726](https://github.com/aml-development/ozp-backend/commit/f66e172606a767ff74cdbeb35b4c8c3d342b62a2))
  *  Added Images, added listing yaml ([ed579c78](https://github.com/aml-development/ozp-backend/commit/ed579c78ad1c599118906b67cf2e6980f0c09699))
  *  Review Suggestion changes ([117e96ea](https://github.com/aml-development/ozp-backend/commit/117e96ea58c5b976591362b150fe49adfbe99775))
  *  Fixed failing screenshot string conversion unittest ([a916a035](https://github.com/aml-development/ozp-backend/commit/a916a035593e6eadb98cfd2aea897d15d3c134fc))
  *  Added original pictures back to scripts directory ([bee7c0fc](https://github.com/aml-development/ozp-backend/commit/bee7c0fcce9d8dd7c6dc02ec781a863283252bd1))
  *  Refactored Images ([d08150cd](https://github.com/aml-development/ozp-backend/commit/d08150cdc5b81e4607c7d98e523f44a57c509d77))
  *  Added Generic Screenshots to every listing ([5b1d63fe](https://github.com/aml-development/ozp-backend/commit/5b1d63fee1f6e9937e72ee73b9888e6d7b62e86a))
  *  Refactored Sample Data Generator ([31fce58c](https://github.com/aml-development/ozp-backend/commit/31fce58c9488c5f9afc5411eb08046d58da3d8f6))     
* refactoring: Refactor sample data generator ([55d5b2c9](https://github.com/aml-development/ozp-backend/commit/55d5b2c94d57b6895c31b186f4b63ee68a2356d3))    

#### Merge Pull Requests  
* Merge pull request #337 from aml-development/addingNeededFields ([893e63e6](https://github.com/aml-development/ozp-backend/commit/893e63e6f0c5387570ddbd988b6929ffe9a3c48f))
* Merge pull request #336 from aml-development/es_recommend_content ([64b22118](https://github.com/aml-development/ozp-backend/commit/64b22118d2816412ba8afa7aa80312fc81c69a64))
* Merge branch 'master' into es_recommend_content ([44e2b6bd](https://github.com/aml-development/ozp-backend/commit/44e2b6bd3f6a24374e768f24e506a2795310d2e3))
* Merge pull request #334 from aml-development/simplify_storefront_1 ([2e1e24e8](https://github.com/aml-development/ozp-backend/commit/2e1e24e82076a958fc12f9ed881801cba5850dcb))         

#### Changes  
* added needed fields for bookmarking and display ([78198550](https://github.com/aml-development/ozp-backend/commit/78198550c596e9694890d45326d35b0f39993a52))     

### 1.0.69 (2017-08-02)

#### Feature 
* **es_recommend**
  *  Changed Boost value from 10 to 2 for ratings to prevent high ratings from flooding recommendations. ([b0527353](https://github.com/aml-development/ozp-backend/commit/b0527353746ab835860f4622277575092fc7a303))
  *  Added code to put correct content based recommendations into list.  Need to verify content is coming out correctly. ([f2915c57](https://github.com/aml-development/ozp-backend/commit/f2915c57994a45a6f4fb007543d8c3c97c7c3edb))      

#### Refactor 
* **storefront**
  *  Refactor Duplicate Code ([ba70526a](https://github.com/aml-development/ozp-backend/commit/ba70526aaa20da516842bc49964c56fc924f70a8))
  *  Simplify Storefront to use less fields ([e07b39a2](https://github.com/aml-development/ozp-backend/commit/e07b39a2bf263ca799d948dec8c99737e821d21a))
  *  Ability to only retrieve sub keys from storefront ([a5cbd9b0](https://github.com/aml-development/ozp-backend/commit/a5cbd9b04f18e8dbd24fe25ea03dc00c2293ecac))     

#### Merge Pull Requests  
* Merge pull request #333 from aml-development/ratings_boost_fix ([5183e842](https://github.com/aml-development/ozp-backend/commit/5183e842439c5f4e502b463165cfe723a433b4e4))
* Merge pull request #332 from aml-development/simply_storefront ([8af4cc80](https://github.com/aml-development/ozp-backend/commit/8af4cc80071ca22417f365e11dcdca5b6454a4ce))           

### 1.0.68 (2017-07-26)

#### Feature  
* **storefront**:  Created ViewSet for Storefront ([be8563eb](https://github.com/aml-development/ozp-backend/commit/be8563ebe6d16f9b122398428bf2a50cbbab7d95))    
* **es_recommend_content**:  Initial working model that needs to be vetted ([15e25ad4](https://github.com/aml-development/ozp-backend/commit/15e25ad459c13a80d045d113fa711874bdb2c0cc))    
* **recommend_es_content**:  Changes for adding content information to user tables and clean up. ([70e45758](https://github.com/aml-development/ozp-backend/commit/70e4575882e8b38325efe9b6d55b5c903b799831))    
* **sample_data**:  Added Elasticsearch Mapping Check ([7b76b806](https://github.com/aml-development/ozp-backend/commit/7b76b806afdfaebba3ff855af4d2c4bc15683290))   
* **organization**
  *  Add short name sorting for organization in metadata endpoint ([36fdfaa2](https://github.com/aml-development/ozp-backend/commit/36fdfaa215b8c553d20b88fe6405e2a038a430af))
  *  Sort organizations by title ([232228b1](https://github.com/aml-development/ozp-backend/commit/232228b16cc8f971217215073f48460c903c8738))     
* **search**:  Tweaked Min_score ([136cd378](https://github.com/aml-development/ozp-backend/commit/136cd3787ebdf00945c6eb7196b54adfb0b246fb))    

#### Fixes  
* **category**:  Change error message ([f25f439a](https://github.com/aml-development/ozp-backend/commit/f25f439a0f491a14c3e2e9725c2fc68c9fff388c))    

#### Refactor  
* **search**:  Added Documentation, Corrected Mapping ([c4307c1f](https://github.com/aml-development/ozp-backend/commit/c4307c1fe02aa5503c4a1ecf8f5f663ec36d93e8))    

#### Merge Pull Requests  
* Merge pull request #331 from aml-development/sample_data ([b28f1b79](https://github.com/aml-development/ozp-backend/commit/b28f1b79fb4a1e1ad18983739c26e6291f7eb45a))
* Merge pull request #330 from aml-development/category_confirmation ([f0ea1867](https://github.com/aml-development/ozp-backend/commit/f0ea18675ec921ea1898ab5b7e839ba1925ee7f7))
* Merge pull request #328 from aml-development/organization_sort ([8962d53a](https://github.com/aml-development/ozp-backend/commit/8962d53a2b3aa28c958bf87f84db70301661b66a))
* Merge pull request #326 from aml-development/search_refactor ([0fcf7c34](https://github.com/aml-development/ozp-backend/commit/0fcf7c34f9575d683363c8c471378ae13baad0d7))
* Merge pull request #327 from aml-development/organization_sort ([1ac5c3b2](https://github.com/aml-development/ozp-backend/commit/1ac5c3b281f7ebbb84f2640a04c6a4419ea74206))         

#### Changes  
* Merge from Main and update for ozpcenter/recommend/recommend.py ([c1d07936](https://github.com/aml-development/ozp-backend/commit/c1d07936767ffb9734a4c85c29c029a0cca4fbe9))
* (es_recommend) Port changes from es_recommend_user branch ([904a5b36](https://github.com/aml-development/ozp-backend/commit/904a5b367a8ab8f97ddad7d44a9002ea5fb64574))     

### 1.0.67 (2017-07-19)

#### Feature  
* **order**:  Allow title sorting to do case insensitive sort ([11193d7f](https://github.com/aml-development/ozp-backend/commit/11193d7feae4c99da6e65484f37acf87d832bdaa))    

#### Fixes  
* **order**:  Re-add approved date for latest sort option ([6c3c338c](https://github.com/aml-development/ozp-backend/commit/6c3c338c496d395fa00f44f2aef38de6ea51b344))    

#### Refactor  
* **search**:  Added Documentation to method ([f01741fb](https://github.com/aml-development/ozp-backend/commit/f01741fb0939fa3d67e8735e1bf27d16c6ae7d53))    

#### Merge Pull Requests  
* Merge pull request #325 from aml-development/refactor ([6a5057cf](https://github.com/aml-development/ozp-backend/commit/6a5057cf3e50b8bc45852bc59fcd8a4fa70b9e5c))           

### 1.0.66 (2017-07-12)

#### Feature 
* **order**
  *  Fixed Title Order for Search ([0d87064e](https://github.com/aml-development/ozp-backend/commit/0d87064e74cf499b372218b093b4896e6d3d93aa))
  *  Added Ordering to ES_Search ([0546591d](https://github.com/aml-development/ozp-backend/commit/0546591d86cf2925842b85aaa624757c17516281))     

#### Fixes 
* **notification**
  *   Added More Documentation, Subscription Notification when listing gets published ([014b8da1](https://github.com/aml-development/ozp-backend/commit/014b8da1055b562f75de9070aeada24298446826))
  *  Fixed add_subscription_notification ([b80abab9](https://github.com/aml-development/ozp-backend/commit/b80abab9b565418f71f2ead96d09b11aff498524))     
* **notifications**:  Listing Review Preference Flag Filter (#323) ([5a584199](https://github.com/aml-development/ozp-backend/commit/5a58419966851337f3ada64914499c00fd76ccff))     

#### Merge Pull Requests  
* Merge pull request #324 from aml-development/fix_permission ([41b3534e](https://github.com/aml-development/ozp-backend/commit/41b3534e69556a3520ef1ad7a346ce03bb15d15b))           

### 1.0.65 (2017-07-04)

#### Feature  
* **preference**:  Listing ([27f23dab](https://github.com/aml-development/ozp-backend/commit/27f23dabcb063f08c0eee7869f1542d4b8bb3ab0))      

#### Merge Pull Requests  
* Merge pull request #320 from aml-development/users ([16b3a079](https://github.com/aml-development/ozp-backend/commit/16b3a079063da7f96a4d10f7e2cc0ad34fe21097))           

### 1.0.64 (2017-06-28)

#### Feature 
* **profile**
  *  Added more documentation ([f842cf02](https://github.com/aml-development/ozp-backend/commit/f842cf029c4afc627c8180a1c1b13a049f4989e3))
  *  Added Ability to update groups, email flag, stewards group for profile ([751919ad](https://github.com/aml-development/ozp-backend/commit/751919ad43e647a757572c4ca1b40401641db58b))     
* **es_recommend**:  Corrected weight to mix well with other recommendation engines and added more comments. ([ceaa7270](https://github.com/aml-development/ozp-backend/commit/ceaa7270e2af1c76e1b66b9a5f19bd01c7fabb67))    
* **email**:  Added Email Varibles to Settings.py ([407ad9ab](https://github.com/aml-development/ozp-backend/commit/407ad9abe8f2873dadec3c6c61a390c12ebe63cd))    
* **users**:  Added Users Doc in yaml ([92f2d64e](https://github.com/aml-development/ozp-backend/commit/92f2d64e82e5d00e88ee17b0ff1362ad6e720650))    

#### Fixes  
* **profile**:  Fixed Unittest for profiles ([4341b5f8](https://github.com/aml-development/ozp-backend/commit/4341b5f8295580d6f1e6d586607ad86e4402f734))    
* **travis-ci**:  Fixed hang ([a95011cc](https://github.com/aml-development/ozp-backend/commit/a95011ccd678c5796d48d69b50fdc08255aacfb3))     

#### Merge Pull Requests  
* Merge pull request #317 from aml-development/es_user_categories ([8273f436](https://github.com/aml-development/ozp-backend/commit/8273f436b4760476c2bc34bde6b738c4720969e3))
* Merge pull request #319 from aml-development/email_template ([e47f7eea](https://github.com/aml-development/ozp-backend/commit/e47f7eeaef0378ed291023f9f2050014c7347f42))
* Merge pull request #318 from aml-development/profile_api ([ef62736b](https://github.com/aml-development/ozp-backend/commit/ef62736b78868ef6437bd12c6eac80e9be54e959))         

#### Changes  
* (es_recommend): Added comments and refactored query to have better recommendations ([b974f7ff](https://github.com/aml-development/ozp-backend/commit/b974f7ffeb3de47d256163e21dad942d562aeb8d))
* (es_recommend) Changes to improve code reuse and added change to limit categories for reviews greater than 3 ([b1aa8a41](https://github.com/aml-development/ozp-backend/commit/b1aa8a4157a151b146e7f25dc25630a4e515228d))
* (es_recommend): Added listing_categories to items that should be considered ([9fff15c8](https://github.com/aml-development/ozp-backend/commit/9fff15c8ef38602ec1d68b57ae1358011344fa62))
* (es_recommend): Added Categories to ES User Based Recommendation and increased ratings to 3.5 to be considered for reviews. ([ae2c9f40](https://github.com/aml-development/ozp-backend/commit/ae2c9f40f39f289eefef816e0be00c7308cf8d26))     

### 1.0.63 (2017-06-21)

#### Feature 
* **category**
  *  Improve Error Handling ([304a17f8](https://github.com/aml-development/ozp-backend/commit/304a17f863ac8d94a4e178d510ed906afcbcea92))
  *  Added Deletion Validation ([4baa6c5f](https://github.com/aml-development/ozp-backend/commit/4baa6c5f2b90ee998f3f005396625d8e557cf9c1))     

#### Fixes  
* **notifications**:  Sort notifications by created date ([07630cad](https://github.com/aml-development/ozp-backend/commit/07630cad708604166708222552a5345806e27a35))     

#### Merge Pull Requests  
* Merge pull request #316 from aml-development/active_notification_bug ([d487ecb7](https://github.com/aml-development/ozp-backend/commit/d487ecb7d2760cdb9d08765c82c7d5c3b1e32907))
* Merge pull request #315 from aml-development/category_valid ([856e20f8](https://github.com/aml-development/ozp-backend/commit/856e20f84f2653bcdc47ab260e2174d869b2c863))
* Merge pull request #314 from aml-development/es_recommend_user_latest ([675362af](https://github.com/aml-development/ozp-backend/commit/675362afc03c5948c55db7e0123693655e4bc690))         

#### Changes  
* (es_recommend) Port changes from es_recommend_user branch ([8998ff3c](https://github.com/aml-development/ozp-backend/commit/8998ff3c291ccdf97632d27e723c77d57d94ddfd))     

### 1.0.62 (2017-06-15)

#### Feature 
* **recommend**
  *  Fixed typo in storefront ([4b1d837f](https://github.com/aml-development/ozp-backend/commit/4b1d837f30bc12827d1446f1b318a349a27c2482))
  *  Fixed hardcoded username ([6ff1b615](https://github.com/aml-development/ozp-backend/commit/6ff1b615b71334b179d372a4f1367d5e394d0479))       

#### Merge Pull Requests  
* Merge pull request #313 from aml-development/recommend_type ([58a4352c](https://github.com/aml-development/ozp-backend/commit/58a4352cc1ae7aa8082dff2ed9b96454d5bf02b6))
* Merge pull request #312 from aml-development/fix_recommendation ([55ba3b7c](https://github.com/aml-development/ozp-backend/commit/55ba3b7c6b9e7b5c14e311920d141bbc47bac959))           

### 1.0.61 (2017-06-13)

#### Feature  
* **email**:  Initial Push for Notifications Email ([dc45d114](https://github.com/aml-development/ozp-backend/commit/dc45d11497bb8ec996e9f603959ca89bccf3fefc))    

#### Fixes  
* **recommend**:  Fixed Ordering and added scores to entry ([13f4942f](https://github.com/aml-development/ozp-backend/commit/13f4942f59f2b676451ec3a9950cbd36673f3429))     

#### Merge Pull Requests  
* Merge pull request #310 from aml-development/email-notify ([ded00292](https://github.com/aml-development/ozp-backend/commit/ded002921e229033cbe7e918a2ef75d06bff89c1))
* Merge pull request #311 from aml-development/recommendation_scores ([743a8b33](https://github.com/aml-development/ozp-backend/commit/743a8b33b558feb2ae8d6dc4b1d2570ca21fe2fa))         

#### Changes  
* Notification endpoint update (#291) ([c5c00aa3](https://github.com/aml-development/ozp-backend/commit/c5c00aa38514c79f6e103f89b33f3c5b8a81a555))     

### 1.0.60 (2017-06-07)

#### Feature 
* **recommend**
  *  Added Non-random beginning number ([0a6bbd26](https://github.com/aml-development/ozp-backend/commit/0a6bbd269b5836d71fdf6b3bbe7595bcf8c87ea9))
  *  Added Jittering Pipe for Storefront ([aea0465e](https://github.com/aml-development/ozp-backend/commit/aea0465ef0951c43a68e07c480b040b5e6758fe0))       

#### Merge Pull Requests  
* Merge pull request #308 from aml-development/syntaxy ([35723f47](https://github.com/aml-development/ozp-backend/commit/35723f47599cf675d8847bd19bfb77d0a50cc3b0))
* Merge pull request #309 from aml-development/tag_subscription ([f9eceb5c](https://github.com/aml-development/ozp-backend/commit/f9eceb5c17aa5e61b6b6363a332e741c7f9f819b))
* Merge pull request #306 from aml-development/jitter ([b37f4459](https://github.com/aml-development/ozp-backend/commit/b37f44598b13fd12e9926420ae6b1b0a5054a65a))         

#### Changes  
* Updating test cases for new notifications ([2c7c2a49](https://github.com/aml-development/ozp-backend/commit/2c7c2a496dad462fda845c4248f8c59049d9d9c1))
* Updating the language for notifications. Adding some html styling to listing names ([1e087784](https://github.com/aml-development/ozp-backend/commit/1e0877840e97328e8e7ea1693aa119416978cf18))
* Changing the listing changes message to look less syntaxy. ([418b60b5](https://github.com/aml-development/ozp-backend/commit/418b60b5dcdc91b2e740141ec33de867bec8e3c3))
* Add id field for tag ([463b7fc1](https://github.com/aml-development/ozp-backend/commit/463b7fc11178695469fcd1a38370a5ff1d00786b))     

### 1.0.59 (2017-05-31) 

#### Fixes 
* **recommend**
  *  Syntax Fix) ([0d570e45](https://github.com/aml-development/ozp-backend/commit/0d570e45295222845e440a56b47dc1d8528797bf))
  *  Fixed Caching Issue for dynamic checking of bookmarked recommended apps ([f7b82bff](https://github.com/aml-development/ozp-backend/commit/f7b82bff609dc5facb107574cd89782aa4e861fa))      

#### Merge Pull Requests  
* Merge pull request #305 from aml-development/mannyrivera2010-patch-1 ([3da140b3](https://github.com/aml-development/ozp-backend/commit/3da140b34eb724964656b81977a3b0657e581fda))
* Merge pull request #304 from aml-development/recommender_bookmark_removal ([fc4fe090](https://github.com/aml-development/ozp-backend/commit/fc4fe090efa3e578b9db1fe48764947a76298141))         

#### Changes  
* (recommed) Remove Bookmarked Items from list of Recommended Items to display to user ([168b6915](https://github.com/aml-development/ozp-backend/commit/168b69156818676252b809491b810e79b6faa841))     

### 1.0.58 (2017-05-24)   

#### Merge Pull Requests  
* Merge pull request #301 from aml-development/recommender_fix ([dcebfe83](https://github.com/aml-development/ozp-backend/commit/dcebfe833c7ed4bdfbb48d029a2e950eea76c9c4))
* Merge pull request #302 from aml-development/recommender_edge_fix_latest ([f9a2e859](https://github.com/aml-development/ozp-backend/commit/f9a2e85931bdb1d3ed7c95579008834a0c944aa1))         

#### Changes  
* (recommender) Fix for checking for None on Vertex during graph algorithm for recommendations ([1134222c](https://github.com/aml-development/ozp-backend/commit/1134222c5ab81b86835384df15349ce307035eca))
* (recommender) Fix ordering of recommendations ([b61df4af](https://github.com/aml-development/ozp-backend/commit/b61df4afc1dc12e47f15f45fe871db98d4eb0f82))     

### 1.0.57 (2017-05-17)

#### Feature  
* **notify**:  Added Tag and Category subscriptions ([8d379321](https://github.com/aml-development/ozp-backend/commit/8d37932144ed810b6fa80ebd3f802616ada45a06))    
* **sub**:  Refactor Subscription code ([729f4a0b](https://github.com/aml-development/ozp-backend/commit/729f4a0bb2730aa44c3e1700593331ba5d0ae927))   
* **s3**
  *  Cleaned Requirements.txt ([f35292b4](https://github.com/aml-development/ozp-backend/commit/f35292b4098ee8a4a2dae487d2dc1e317c130d2a))
  *  Added Minio Testing Instructions ([2b49e01e](https://github.com/aml-development/ozp-backend/commit/2b49e01ea931a4a56c6d7f382c60692df5913279))
  *  Added S3 Code, scripts, new dependencies ([cbedeadb](https://github.com/aml-development/ozp-backend/commit/cbedeadb59a7b8ed52ea8c5970d42f122d4234bd))       

#### Merge Pull Requests  
* Merge pull request #299 from aml-development/remove_featured_limit ([ed6f0892](https://github.com/aml-development/ozp-backend/commit/ed6f08923fd6f43ff7b3a9955667ddca11af7043))
* Merge pull request #300 from aml-development/sub_notify ([4b2a396e](https://github.com/aml-development/ozp-backend/commit/4b2a396e190d656979019050442e1e015d529368))
* Merge pull request #298 from aml-development/too_many_tabs_data ([ca2a0a69](https://github.com/aml-development/ozp-backend/commit/ca2a0a691ac188c99e3015f6875cec7a1258c1ef))
* Merge pull request #297 from aml-development/s3 ([5b70ef38](https://github.com/aml-development/ozp-backend/commit/5b70ef3884e13a4fa35c8dbb1f10415580611dbe))       

#### Test  
* Test data for too_many_tabs center branch ([fe032323](https://github.com/aml-development/ozp-backend/commit/fe0323235cc3bdc61d67d3cf363790074bc4f1bf))     

#### Changes  
* Update CONTRIBUTING.md ([471b3567](https://github.com/aml-development/ozp-backend/commit/471b356759f1e75050a0fe9ffa0a9839ec4f2382))
* Removing the limit for Featured Listings in Center per AMLNG-414 ([b3339d31](https://github.com/aml-development/ozp-backend/commit/b3339d31d914ca3ef444b6c088d51f3382110c4a))
* Updating unit tests to match new profile data ([24b26730](https://github.com/aml-development/ozp-backend/commit/24b267301d13972c7ed92341748f9bd52f779b19))
* Updating test data and tests for additional Orgs/tabs ([ba236825](https://github.com/aml-development/ozp-backend/commit/ba23682577097580be9c1c46a30ed0f0f9994fe2))     

### 1.0.56 (2017-05-10)

#### Feature 
* **notify**
  *  Added Rejected Deletion Notification ([534fcba5](https://github.com/aml-development/ozp-backend/commit/534fcba5862b0a8ac9d29e420072eb2214f0e67d))
  *  Added Listing Changed Notification ([c65ca01d](https://github.com/aml-development/ozp-backend/commit/c65ca01de4f56bbccd5c24d65a11f0ac34a38de9))
  *  Added new Notification types ([fd5a2b3c](https://github.com/aml-development/ozp-backend/commit/fd5a2b3c99f0cbb270222eea56021ac49fa280bf))     
* **email**:  Added Skeleton Email Script ([6cef76d0](https://github.com/aml-development/ozp-backend/commit/6cef76d076f4e17f6221751cd30eb52f8bcabbb9))    

#### Fixes  
* Fixed Syntax ([d4d8752c](https://github.com/aml-development/ozp-backend/commit/d4d8752c3dd9d1cb13fb7caf785905f0a2940b6e))    
* **notify**:  Fixed failing unittests ([4a4bc8eb](https://github.com/aml-development/ozp-backend/commit/4a4bc8eb92a2e4e73066c082a99b0b3a8d544c0b))    

#### Refactor 
* **notify**
  *  Refactoring model_access ([44b787f1](https://github.com/aml-development/ozp-backend/commit/44b787f1a168e74d80781c909026be5f47a43f51))
  *  Finished Listing Submission Notification ([70f23da4](https://github.com/aml-development/ozp-backend/commit/70f23da4813e3a031cf56106b68bfe81b8b72cbe))     
* **notification**:  Refactoring ([a97a4e96](https://github.com/aml-development/ozp-backend/commit/a97a4e963fbee9fb19eb0b9b22c9892b0a2db97e))    

#### Merge Pull Requests  
* Merge pull request #296 from aml-development/screenshot_description ([8a98eb4e](https://github.com/aml-development/ozp-backend/commit/8a98eb4e82f2bb0619e8196bf5780f6befc45b7f))
* Merge pull request #292 from aml-development/notification_desc ([9de22055](https://github.com/aml-development/ozp-backend/commit/9de22055b2146c89279686a00294ea476ab4f1d1))
* Merge branch 'master' of github.com:aml-development/ozp-backend into screenshot_description ([cca1594a](https://github.com/aml-development/ozp-backend/commit/cca1594a6216bafdcaa8f74633f1e3c30c8f42ba))
* Merge pull request #295 from aml-development/434 ([84ab00e1](https://github.com/aml-development/ozp-backend/commit/84ab00e14bd23430296bbb56222fdce641f73445))         

#### Changes  
* Added todo to refactor sort ([89a6d5b4](https://github.com/aml-development/ozp-backend/commit/89a6d5b4e9c069903af6ceb2943bf8d4f6133685))
* Add new screenshot order migration ([1f598bea](https://github.com/aml-development/ozp-backend/commit/1f598bea91e2b2c8d4b6518540cde9d3c135eab9))
* Remove migrations due to merge conflicts ([8a35915c](https://github.com/aml-development/ozp-backend/commit/8a35915c30a0ff2fbebfa99b6c4c0ce068ad323f))
* Cleanup ([8b8e4b0d](https://github.com/aml-development/ozp-backend/commit/8b8e4b0d944a56cb580c136aa01de13e6aa8a498))
* Update model_access.py ([28021cf3](https://github.com/aml-development/ozp-backend/commit/28021cf398c907ea9c902844c13158b868c04e2c))
* Update model_access.py ([66f7b247](https://github.com/aml-development/ozp-backend/commit/66f7b24728907e2f30a8b366cc448dce9de26079))     

### 1.0.55 (2017-05-03)

#### Feature  
* **screenshot**:  return screenshots in order ([fecef61b](https://github.com/aml-development/ozp-backend/commit/fecef61b1713498ebbd4c752af5611b517e46610))    
* **notification**:  Documentation and added Notification Classes ([d6b5363b](https://github.com/aml-development/ozp-backend/commit/d6b5363bbe3c9badc62cb574119d41671b2db124))    

#### Fixes 
* **groups**
  *  Fixed group logic for unique name ([dfd2f1d1](https://github.com/aml-development/ozp-backend/commit/dfd2f1d16d777f7192fb2e41eff8fbb050245b36))
  *  Added migration script for beta users ([04484c29](https://github.com/aml-development/ozp-backend/commit/04484c29b5c4e20fd415335f8ef432a8d2435f9e))     
* **storefront**:  Reverted back to old way ([c970d9a5](https://github.com/aml-development/ozp-backend/commit/c970d9a540e0ec91828eb29563dc13fa1747313f))    

#### Refactor 
* **notification**
  *  Added group targets ([65ad21c3](https://github.com/aml-development/ozp-backend/commit/65ad21c359c171d583b867d5c60609746c80aa80))
  *  Simplied Logic for adding notification types ([d4cb5c41](https://github.com/aml-development/ozp-backend/commit/d4cb5c41cdc1b3087db811ffb7c6f5fd691edb40))     

#### Merge Pull Requests  
* Merge pull request #294 from aml-development/beta_user_script ([9e93ec37](https://github.com/aml-development/ozp-backend/commit/9e93ec37ab59d4cedd86f27de91ce4c3d3e7aab0))
* Merge pull request #293 from aml-development/storefront_repo ([852cadfe](https://github.com/aml-development/ozp-backend/commit/852cadfe20d93a0e0813131d8825d2e6e89c9ab2))           

### 1.0.54 (2017-04-26)

#### Feature  
* **screenshot**:  initial commit to allow re-arrangement of screenshots ([b4742640](https://github.com/aml-development/ozp-backend/commit/b4742640181c07fa5b74269061cac3113ba3501a))    

#### Fixes  
* **similar_listing**:  Added Lazy loading for listings ([bde388fa](https://github.com/aml-development/ozp-backend/commit/bde388fa08f19f4e21b32f154425666d72aae133))    

#### Refactor 
* **storefront**
  *  Simplied Logic ([42e4d946](https://github.com/aml-development/ozp-backend/commit/42e4d9460d8807b0e8cee9e52f9e94858a174c81))
  *  Added Image URL generation ([297a9fa8](https://github.com/aml-development/ozp-backend/commit/297a9fa8616c9b0650538290e1202213b281e377))
  *  Added more Joins to query ([3dae648e](https://github.com/aml-development/ozp-backend/commit/3dae648e070ea7976f99c4eb9cec08d36ee03f36))
  *  Performance Refactoring ([b0f98308](https://github.com/aml-development/ozp-backend/commit/b0f98308fba49d21c668ae96a51bf92ec99c8da5))     
* **recommend**:  Completed new get_storefront function ([2d02dd64](https://github.com/aml-development/ozp-backend/commit/2d02dd64d764af7a48b116cf9bc9d4cc0d91fc65))    
* **sql**:  Added SQL for User Permissions ([c4c965bc](https://github.com/aml-development/ozp-backend/commit/c4c965bc0901b0b4ba5023627a795e452ebdab50))    

#### Merge Pull Requests  
* Merge pull request #290 from aml-development/recommend_similar_fix ([47f5019f](https://github.com/aml-development/ozp-backend/commit/47f5019fd0aa069f23ded789e4ba4f37d9c6ae4c))
* Merge pull request #289 from aml-development/store_front_per ([b574f285](https://github.com/aml-development/ozp-backend/commit/b574f285717f84ddc2115dfef3faa828a6a9b2ea))         

#### Changes  
* added beta user group for recommendations (#288) ([99de9bbd](https://github.com/aml-development/ozp-backend/commit/99de9bbdc64386f9171157af3d264feb3fae2fa7))     

### 1.0.53 (2017-04-19)

#### Feature  
* **notify**:  Import Performance via Batching ([aeb6d6ed](https://github.com/aml-development/ozp-backend/commit/aeb6d6ed213f70bad7d16c73ab5acdc7d93af8ce))   
* **recommend**
  *  Increased Performance via Batching ([f1df952a](https://github.com/aml-development/ozp-backend/commit/f1df952a8f7c344b7b0c6d9f2dd2a94874b492ca))
  *  Fixed Error incase there are no recommendations ([67495b88](https://github.com/aml-development/ozp-backend/commit/67495b88817d53c3c61c9eecf85389006137b74e))
  *  Added Collabative Filter to recommend script ([43a7627a](https://github.com/aml-development/ozp-backend/commit/43a7627a44d65d12ea25e555f28b05a6cf1278c8))     
* **data**:  Added Bio to profile test data ([043e2553](https://github.com/aml-development/ozp-backend/commit/043e2553d0f52c26afa7d5f5c49dacf1421e9a9d))    
* **sample_data**:  Refactored Sample Data Generator ([369e959c](https://github.com/aml-development/ozp-backend/commit/369e959cddbf55097ca4cd8fc034e55c56959634))   
* **notifications**
  *  Added MiniLove Org_Steward ([2f0630f0](https://github.com/aml-development/ozp-backend/commit/2f0630f03d8718da697e652b1b96f298dc7a82a7))
  *  Fixed Syntax Issue ([cc64a887](https://github.com/aml-development/ozp-backend/commit/cc64a8870df1dd0ec6df73ef99e3518f1b80885f))    
* **notification**
  *  Added new owner field and unittests ([a368920a](https://github.com/aml-development/ozp-backend/commit/a368920a9d32962beb40b51f6ca2c616e5d8a007))
  *  Added Support for notifying Listing Owners, Org Stewards ([10fffafa](https://github.com/aml-development/ozp-backend/commit/10fffafa4a772e706024775802b07347ed843c27))
  *  Refactored Notification Code ([eb30eedb](https://github.com/aml-development/ozp-backend/commit/eb30eedb5762c5d525354514a8a2f8fba32a09ee))     

#### Fixes  
* Fixing a typo ([bccf26f8](https://github.com/aml-development/ozp-backend/commit/bccf26f8cb2133d76e0aecb001ec7bb3b25b3055))   
* **screenshot**
  *  Fixed bug for PUT when description is null ([80d5882c](https://github.com/aml-development/ozp-backend/commit/80d5882c7e5f3d9c573e280aff26739b300d60d2))
  *  Add new migration ([f1ee2c0c](https://github.com/aml-development/ozp-backend/commit/f1ee2c0c036ef5716974b490943603a4c8dfd300))
  *  Remove conflicting migration ([cbbcba5a](https://github.com/aml-development/ozp-backend/commit/cbbcba5a9e10b861efba06705c622aa34d01a395))     
* **recommend**:  Fixed Unit Test Data Generator ([cffb9a1a](https://github.com/aml-development/ozp-backend/commit/cffb9a1a28db94b5e7c6ebc0ff3d4cd60d8d3f99))    

#### Refactor  
* **makefile**:  Fixed Enviromental Vars ([c330b6bb](https://github.com/aml-development/ozp-backend/commit/c330b6bb92829c8a9f46a513249fad3039bb7daa))    
* **sample_data**:  Increase speed of sample_data_gen ([5e0e857e](https://github.com/aml-development/ozp-backend/commit/5e0e857e5385c6600252dd45f0f2644d28057b56))    
* **travis**:  Put Syntax Checker before tests ([dd24f7a6](https://github.com/aml-development/ozp-backend/commit/dd24f7a6bb3d13488dce5df633fc412cbd62a693))    
* **recommend**:  Refactored Recommendation code ([04260bb4](https://github.com/aml-development/ozp-backend/commit/04260bb4aaab1a1f58f9f71482371f6c857a3a5e))    

#### Merge Pull Requests  
* Merge pull request #285 from aml-development/sub_unit_test ([866bacba](https://github.com/aml-development/ozp-backend/commit/866bacba489e1f5b77beec2f6951736abfaf3086))
* Merge branch 'master' into sub_unit_test ([a5f42d36](https://github.com/aml-development/ozp-backend/commit/a5f42d3696747a151f23cef239406c74385e1212))
* Merge pull request #286 from aml-development/typo_fix ([2959d7a6](https://github.com/aml-development/ozp-backend/commit/2959d7a6de1d662c674d99c290a2783805862612))
* Merge pull request #284 from aml-development/recommend_batch ([eaaf105b](https://github.com/aml-development/ozp-backend/commit/eaaf105b19a17a4c4d0501f259c94e923202f13c))
* Merge pull request #283 from aml-development/screenshot_description ([0e970bad](https://github.com/aml-development/ozp-backend/commit/0e970bad3a07dfd16b6903b470b45146d4bb3634))
* Merge pull request #282 from aml-development/recommend_bug ([267f32dc](https://github.com/aml-development/ozp-backend/commit/267f32dcac99d3f73356600b0edf37373b59edc0))
* Merge branch 'master' into sub_unit_test ([baa840aa](https://github.com/aml-development/ozp-backend/commit/baa840aa59972228647b974c87df476eeab6f9e6))
* Merge pull request #281 from aml-development/recom_coll ([b22ad1db](https://github.com/aml-development/ozp-backend/commit/b22ad1db212ee7ec7dec694cc1ba2f3a7b24ee3d))
* Merge pull request #280 from aml-development/screenshot_description ([64f7c779](https://github.com/aml-development/ozp-backend/commit/64f7c7796837074193d4d86661c9f8bdc39670c2))
* Merge branch 'master' of https://github.com/aml-development/ozp-backend into screenshot_description ([d729efb4](https://github.com/aml-development/ozp-backend/commit/d729efb4ad2129c8cfbe4d518efbd2c3538d71f9))           

### 1.0.52 (2017-04-12)

#### Feature  
* **screenshot**:  Allow screenshots ability to have descriptions ([c8389121](https://github.com/aml-development/ozp-backend/commit/c83891217db53b496377d9496cf02456df265307))   
* **recommend**
  *  Added Filter to model_acess ([783881db](https://github.com/aml-development/ozp-backend/commit/783881db481b659bd6b9c7b47e09cd2481dfa973))
  *  Added Recommender Db Migration ([e267cf82](https://github.com/aml-development/ozp-backend/commit/e267cf8298b42658e024cd5024925f4c8bf02eb9))
  *  Refactored How Recommendations are saved ([5c7ccb53](https://github.com/aml-development/ozp-backend/commit/5c7ccb5325536de384f1ecda4c19abaaecd33302))
  *  Refactor code and added unit test ([7f0730ed](https://github.com/aml-development/ozp-backend/commit/7f0730ed93d02add0fed1fd9915d5fc59d4f9fcc))     

#### Fixes 
* **screenshot**
  *  Fix test cases ([18e9b836](https://github.com/aml-development/ozp-backend/commit/18e9b836a8db0a63b29983a3d9c87890e567f4e7))
  *  Allow editing of description ([f73a18a5](https://github.com/aml-development/ozp-backend/commit/f73a18a5520053c8660c30f233ecc86f127c1e11))      

#### Merge Pull Requests  
* Merge pull request #279 from aml-development/recommend_table ([82b97f69](https://github.com/aml-development/ozp-backend/commit/82b97f696eb2c31fc4be43cff94b340f51fd661f))
* Merge pull request #278 from aml-development/search_es ([5083e573](https://github.com/aml-development/ozp-backend/commit/5083e57357e4003462361a23f64142218b6503d2))         

#### Changes  
* Added tesxt case for null value. ([4773345f](https://github.com/aml-development/ozp-backend/commit/4773345f5fc272ab09b2efb801923581994aef47))
* Added check for null value. ([ebdead2c](https://github.com/aml-development/ozp-backend/commit/ebdead2cdbfe546a7a93b7bfa8942e336b47002c))     

### 1.0.51 (2017-04-05)

#### Feature  
* **notification**:  Added more notification dispatcher events ([decdc403](https://github.com/aml-development/ozp-backend/commit/decdc403dc9d28de466bcbfa0f5fc015973e0747))    
* **subscription**:  Added subscription urls,views,model,serializers ([a55731df](https://github.com/aml-development/ozp-backend/commit/a55731df937c6951610004baf2df1cbae9c792d9))    

#### Fixes 
* **able to use special characters when searching**
  * . ([1296855d](https://github.com/aml-development/ozp-backend/commit/1296855db67ddb96b37f747955b24db9c77489ee))
  * . ([4ce5d26d](https://github.com/aml-development/ozp-backend/commit/4ce5d26d259d793a82516ea0c073b51053e411f9))     
* **subscription**:  Fixed Code Syntax ([855e503f](https://github.com/aml-development/ozp-backend/commit/855e503fa95b28f52b74a7ef6535b5d3a19b3401))     

#### Merge Pull Requests  
* Merge pull request #275 from aml-development/subscription ([ceab30c8](https://github.com/aml-development/ozp-backend/commit/ceab30c8adf0ddefa7c526135ecdae331a6d26e6))
* Merge pull request #274 from aml-development/similar_listings ([75e9aee3](https://github.com/aml-development/ozp-backend/commit/75e9aee37d4ef63af3ede271d476a0a4a4bd932b))         

#### Changes  
* Added test case.  Made other minor fixes. ([811bff3c](https://github.com/aml-development/ozp-backend/commit/811bff3c652949bb12f419d7b59397d83bf9c963))
* corrected similar listings returning duplicates ([dfb4a26a](https://github.com/aml-development/ozp-backend/commit/dfb4a26a127b87049e6dbc3dd731509c0f26dc58))     

### 1.0.50 (2017-03-29)

#### Feature  
* **db**:  Added postgresql to MakeFile and Settings.py ([9cdc9520](https://github.com/aml-development/ozp-backend/commit/9cdc95200f69b53582833457465acbfd2ae083ad))   
* **notification**
  *  Added Profile Auth Observer ([689e9a48](https://github.com/aml-development/ozp-backend/commit/689e9a48fe753adf6942638aac36b5f781dec1dd))
  *  Added listing_private_status_changed logic ([272ba5b2](https://github.com/aml-development/ozp-backend/commit/272ba5b2700645f1579c7a3e76aeae4c5b8f1806))
  *  Worked on Listing Observer Class ([5920157b](https://github.com/aml-development/ozp-backend/commit/5920157b0de1d087617fc2bb310521b46fce9af8))
  *  Refactored Dispatcher ([c6ea8c19](https://github.com/aml-development/ozp-backend/commit/c6ea8c19d43a9c8c3cfe6e5ff0e7d1f7287ba8eb))
  *  Started Dispatcher for system events ([fe2ca79e](https://github.com/aml-development/ozp-backend/commit/fe2ca79ee8f009838a42309af23a5447257428ec))
  *  Fixed Notication Fill Migration to include peer id ([5dce907a](https://github.com/aml-development/ozp-backend/commit/5dce907a5b0bdb455906ea29f2084036b3efbd74))
  *  Refactored notification model access ([93d60c25](https://github.com/aml-development/ozp-backend/commit/93d60c257bc93a51207e8151bae71db8cd5222c4))
  *  Simplified Notification Permissions ([778d986f](https://github.com/aml-development/ozp-backend/commit/778d986f7838596f937ee39e965a8e37d1d60532))
  *  Removed Commented Code for NotificationV2 ([8d4dd46b](https://github.com/aml-development/ozp-backend/commit/8d4dd46b642eb1add894434d6f90c7df2752b63b))
  *  Added Db Index for Entity Type and Fixed Unit Test ([07b3df93](https://github.com/aml-development/ozp-backend/commit/07b3df93d7aeec27f02811125415af4059aa4261))
  *  Refactoring Unit Test, Fixed Target list Function ([eb547e7d](https://github.com/aml-development/ozp-backend/commit/eb547e7d5113a6e1bb286a57c0f9867981f1dedf))
  *  Added Notification Mailbox Model and migration scripts ([6baf089b](https://github.com/aml-development/ozp-backend/commit/6baf089b24152393f63f1fa8e30287ccc3712e86))     
* **setup**:  Added new packages into setup.py ([ea2c3311](https://github.com/aml-development/ozp-backend/commit/ea2c33114abc922689e4b9ebb19ad823347d5041))      

#### Merge Pull Requests  
* Merge pull request #273 from aml-development/notification_postgres ([80993ce8](https://github.com/aml-development/ozp-backend/commit/80993ce8f6369ef9a13544e3729b4a6a7c66a03d))
* Merge pull request #272 from aml-development/notification ([42741d55](https://github.com/aml-development/ozp-backend/commit/42741d554cc20704d6c91d93ecab4b51322e3ad9))
* Merge branch 'master' into notification ([7add6d76](https://github.com/aml-development/ozp-backend/commit/7add6d7689443621c73dafd4ab8f9526e28e3434))           

### 1.0.49 (2017-03-22)

#### Feature 
* **notification**
  *  Refactored Notification to include notification_type, group target ([a2678ff5](https://github.com/aml-development/ozp-backend/commit/a2678ff5c892bcd2b5d466adc61056c019464da1))
  *  Refactor Migration Script, added flake8 to scripts ([e5db398d](https://github.com/aml-development/ozp-backend/commit/e5db398d62bb0016280555ebe8dfafb3e79c71a0))
  *  Added NotificationV2 Model and migration scripts ([ba23744a](https://github.com/aml-development/ozp-backend/commit/ba23744ae10fa4b98dc93d154924d54ecc9d19fd))     
* **library**:  Fixed Unit test ([55e18d0e](https://github.com/aml-development/ozp-backend/commit/55e18d0ec18423319177c740dc51c312b03010c7))    
* **recommend**:  Enriched sample data and unit test ([60344cd3](https://github.com/aml-development/ozp-backend/commit/60344cd3669754705b24aa3c46070726311f04ab))    

#### Fixes 
* **elasticsearch**
  *  Removed extra comma ([d2b76bf3](https://github.com/aml-development/ozp-backend/commit/d2b76bf3833712c7632e4826dff95df99265d64d))
  *  fixed elasticsearch mapping for tags ([c9a68571](https://github.com/aml-development/ozp-backend/commit/c9a68571451f17de8fd11b4c647047badd9486c7))     
* **unittest**:  Fix unit tests ([2de48dc5](https://github.com/aml-development/ozp-backend/commit/2de48dc530cb4e79db8ba31226a84f4f9038ac8f))     

#### Merge Pull Requests  
* Merge pull request #271 from aml-development/es_fix_tags ([0ef364b6](https://github.com/aml-development/ozp-backend/commit/0ef364b6998767a63bf6c9bc6205e5eba147d6f2))
* Merge pull request #270 from aml-development/api_info ([f4efb29a](https://github.com/aml-development/ozp-backend/commit/f4efb29a37a1bc6038f5e33122b6ac619b2439e7))
* Merge branch 'master' of https://github.com/aml-development/ozp-backend into api_info ([4ef79645](https://github.com/aml-development/ozp-backend/commit/4ef79645ad88d9e977629294a584b29cac52e040))
* Merge pull request #269 from aml-development/graph_impl_refactor ([ca85ba7b](https://github.com/aml-development/ozp-backend/commit/ca85ba7b0ba7999087fc5e4ab8912fb8b0aedd6b))         

#### Changes  
* dkdk ([2ae4a2a7](https://github.com/aml-development/ozp-backend/commit/2ae4a2a7bc1ac92a211fd139a4f4ac51e4f0c74d))
* Updated API Documentation again. ([00321a3e](https://github.com/aml-development/ozp-backend/commit/00321a3e1bc2fb6fdb948ae371992641b33386d0))
* Updated API Documentation. ([b3e93105](https://github.com/aml-development/ozp-backend/commit/b3e93105099689f26f2cfcdd322258945bc6b393))
* Added API Documentation. ([fcc5ff8d](https://github.com/aml-development/ozp-backend/commit/fcc5ff8df86b6455cda07ee008be983ebf1032e5))    
* **cleanup**:  Cleaned up print statements ([35be6961](https://github.com/aml-development/ozp-backend/commit/35be6961e20ec8bda37f0b5962acf90c71151c71))    
* **readme**:  Added ReadMe to elasticsearch ([3ff7f59e](https://github.com/aml-development/ozp-backend/commit/3ff7f59e99f7cf13b0eb5816aa036ad590e5ade2))     

### 1.0.48 (2017-03-15)

#### Feature 
* **recommend**
  *  Ability to merge recommendation engine results ([bdc28505](https://github.com/aml-development/ozp-backend/commit/bdc2850597fdb632d76c52e6721b03d3107a05a1))
  *  Added more unit test ([1a073723](https://github.com/aml-development/ozp-backend/commit/1a073723f060e963891b442c0a00bccda8e0e202))
  *  Finished Graph Algorithm ([aa6fb153](https://github.com/aml-development/ozp-backend/commit/aa6fb153942dd190d8c5f35e8d388780fa35bf14))
  *  Added Graph Algorithm Class ([c45bb811](https://github.com/aml-development/ozp-backend/commit/c45bb8116c1ef6b7ff783aaf809d0bf1ddc487a7))
  *  Fixed Syntax ([3ae39a74](https://github.com/aml-development/ozp-backend/commit/3ae39a748aa135c5b2b1b91cabe19288e8adfb9c))
  *  Finished Graph Collaborative Filter ([572ca34c](https://github.com/aml-development/ozp-backend/commit/572ca34ca10be4826f12f94cf437514441a21cac))
  *  Out Pipe and unit tests ([3e1c6234](https://github.com/aml-development/ozp-backend/commit/3e1c62341e5f398baac598c060dae867c8309a27))       

#### Merge Pull Requests  
* Merge branch 'master' into graph_impl_refactor ([5ccc8e9b](https://github.com/aml-development/ozp-backend/commit/5ccc8e9bef65fe551a0e05f1c1bbc6df4382a6df))
* Merge pull request #268 from aml-development/graph_implementation ([703494e4](https://github.com/aml-development/ozp-backend/commit/703494e47aff117ba8cbbbb1757ebd8c1307d44c))           

### 1.0.47 (2017-03-08)

#### Feature  
* **recommend**:  Graph Edge Implementation ([fc7564c0](https://github.com/aml-development/ozp-backend/commit/fc7564c05eddc662c1cda71604943c4df4bad917))    

#### Fixes  
* fixed syntax ([b414a895](https://github.com/aml-development/ozp-backend/commit/b414a895bac2e2f329c0ea3240696be24ce27d76))
* fixed syntax ([d362373d](https://github.com/aml-development/ozp-backend/commit/d362373d6226c5dcbb1d090eeb405ab8042cf391))     

#### Merge Pull Requests  
* Merge pull request #267 from aml-development/graph_impl ([5d1f521a](https://github.com/aml-development/ozp-backend/commit/5d1f521a3d656082b42d9c58023f2f0b39535e71))         

#### Changes  
* commented out unused imports ([5688af64](https://github.com/aml-development/ozp-backend/commit/5688af645323fd9e43187d143fd72735b5c1ec6a))     

### 1.0.46 (2017-03-04)   

#### Merge Pull Requests  
* Merge pull request #265 from aml-development/tags ([61fcee25](https://github.com/aml-development/ozp-backend/commit/61fcee25b15faa290e8ba3bb38be1d453529fcda))           

### 1.0.45 (2017-03-02)

#### Feature 
* **performance**
  *  Corrected Variable names ([7a723256](https://github.com/aml-development/ozp-backend/commit/7a72325675946779ad14a2151e9afbd36bc5edc3))
  *  Added Pipes ([5c3b35ea](https://github.com/aml-development/ozp-backend/commit/5c3b35ea60095c634de6343fcd9263ce0a78d5e5))
  *  Fixed Performance ([94aceb2e](https://github.com/aml-development/ozp-backend/commit/94aceb2e202a577271c439a52c1baec5191b8398))       

#### Merge Pull Requests  
* Merge pull request #266 from aml-development/performance ([a994ca09](https://github.com/aml-development/ozp-backend/commit/a994ca092edf246fabb74bbe85fbac746804cdbf))           

### 1.0.44 (2017-03-02)

#### Feature  
* **recommend**: Lazy Security Marking Check and unit tests ([1a91d913](https://github.com/aml-development/ozp-backend/commit/1a91d913c821d67137a80837ac678f94613bcfc3))    

#### Fixes  
* (fix):Added the ability to search tags. ([519dac2b](https://github.com/aml-development/ozp-backend/commit/519dac2be1a80df5de3d815f6d1404bfc26f3908))     

#### Merge Pull Requests  
* Merge pull request #264 from aml-development/recommend_listings ([a2ab20b9](https://github.com/aml-development/ozp-backend/commit/a2ab20b97b1a14a6b7e59fe203103ddb048b7ea1))         

#### Changes  
* Removed "tags.name^ + str(btg)" from the fields key. ([d09db0be](https://github.com/aml-development/ozp-backend/commit/d09db0befa886922e5e1a87562cd7887432f3f0b))     

### 1.0.43 (2017-03-01)

#### Feature  
* **similar**:  Finished Endpoint for Similar Listings ([250911dd](https://github.com/aml-development/ozp-backend/commit/250911dd10b056b791fe021c39f7cef2e30caece))   
* **recommend**
  *  Query Builder and tests ([c66e6d29](https://github.com/aml-development/ozp-backend/commit/c66e6d294aa103f2a88edd9e8deec039e7df8811))
  *  Verbose Progress ([e6b6b938](https://github.com/aml-development/ozp-backend/commit/e6b6b938b033a07de815fdf1df7adb30d43b05b3))     
* **elasticsearch**:  Worked on Graph Workflow code ([045705fb](https://github.com/aml-development/ozp-backend/commit/045705fb99176cad86fb2bf92d1a9e6775eab36f))    

#### Fixes 
* **elasticsearch**
  *  Fixed build syntax issues. ([ae623a59](https://github.com/aml-development/ozp-backend/commit/ae623a5975639df2e3cbd7bc44804177db196627))
  *  Fixed Tags filtering ([05f059e0](https://github.com/aml-development/ozp-backend/commit/05f059e016528930bdadcf65630153653b7d6ea9))      

#### Merge Pull Requests  
* Merge pull request #262 from aml-development/recommend_graph ([ad8dd16e](https://github.com/aml-development/ozp-backend/commit/ad8dd16e7b5cbc36e19b695f53bac6c5ada3148b))
* Merge pull request #263 from aml-development/tags ([b3ff53b0](https://github.com/aml-development/ozp-backend/commit/b3ff53b0972770f9c2b6e4e32537e8ee9568d694))
* Merge pull request #258 from aml-development/listing_similar ([661874e5](https://github.com/aml-development/ozp-backend/commit/661874e5f1ef0cd4daef7582711ee8b1b8046e32))
* Merge pull request #261 from aml-development/recommend_progress ([dc1d3526](https://github.com/aml-development/ozp-backend/commit/dc1d3526be3699bf021ab0786a45b830e2368284))           

### 1.0.42 (2017-02-27)

#### Feature 
* **elasticsearch**
  *  Fixed mutable default arguments ([aa877fa9](https://github.com/aml-development/ozp-backend/commit/aa877fa9850a1b653ab844a19a94995d823da678))
  *  Added infomation on relevance algorithms ([3c403c53](https://github.com/aml-development/ozp-backend/commit/3c403c538b041de3b94fb27da3f7d62fc6ca8e72))
  *  Added more information about algorithms ([b9e38c0a](https://github.com/aml-development/ozp-backend/commit/b9e38c0a8d6934db02e78c0b9c67fb9be8456a08))
  *  Added Sorting for CustomHybridRecommender ([28c754a4](https://github.com/aml-development/ozp-backend/commit/28c754a41a5d0dc60a9416e642b63a05f108f74c))
  *  Added Collaborative Filtering Algorithm Idea ([d6ed6ec5](https://github.com/aml-development/ozp-backend/commit/d6ed6ec520daf2ca63974596e0ba7ee17d57e93d))
  *  Started work on Graph Implementation ([c06db736](https://github.com/aml-development/ozp-backend/commit/c06db736f01fba5912925183729b019f0fdbf799))
  *  Added Unit Tests for Recommend Utils File ([2f4e31b4](https://github.com/aml-development/ozp-backend/commit/2f4e31b4fc5df3e727d5ba0a9349583fab2d2b34))
  *  Added Utils File for static functions ([62e2c4a8](https://github.com/aml-development/ozp-backend/commit/62e2c4a826c24faaa76e94610d7928d10a3e0b72))
  *  Refactored, fixed weights ([b4d957a3](https://github.com/aml-development/ozp-backend/commit/b4d957a38343a73cfcfbf04f4528abe88e95d8d7))    
* **recommend**
  *  Fixed Typo for listing_id db_save function ([d6606fd2](https://github.com/aml-development/ozp-backend/commit/d6606fd2e7ef10540e648a81a06215fab1c5dc74))
  *  Added Custom Recommender ([aea6deb7](https://github.com/aml-development/ozp-backend/commit/aea6deb786b340a28cc06d1b75c380de24e3f353))
  *  Added Logger and Elasticsearch Template code ([13964cd9](https://github.com/aml-development/ozp-backend/commit/13964cd950e61cb3a0557ad81d6b7023cf863c6d))       

#### Merge Pull Requests  
* Merge pull request #260 from aml-development/recommender_custom ([e251a26d](https://github.com/aml-development/ozp-backend/commit/e251a26d5e114988b77b52dd03424880e65b930c))
* Merge pull request #259 from aml-development/recommender_crab ([3515b11e](https://github.com/aml-development/ozp-backend/commit/3515b11e4b412b568d8e4a35e8af027e4fb3b07c))           

### 1.0.41 (2017-02-22)

#### Feature  
* **listing**:  Added Route and Template for Similar Listings ([406e3fea](https://github.com/aml-development/ozp-backend/commit/406e3fea88c11e9eb0713f8d1caf02d215c88a45))   
* **recommend**
  *  Added Recommend Runner Script ([2cd46528](https://github.com/aml-development/ozp-backend/commit/2cd46528e5dda66ccca3787b4210a4ed169b866f))
  *  Cleaned up code, Added script to run engine ([4b1bacfe](https://github.com/aml-development/ozp-backend/commit/4b1bacfe29c17360d5105b3654d02b054da968d4))
  *  Added recommender wrapper class ([45083bc3](https://github.com/aml-development/ozp-backend/commit/45083bc35a44c6e08d890d890749eb802b5143f0))
  *  Added recommender template code ([03086fa7](https://github.com/aml-development/ozp-backend/commit/03086fa7c632d5611b2e7fcca33125afb7556a3c))       

#### Merge Pull Requests  
* Merge pull request #257 from aml-development/recomender_er_1 ([d9e94669](https://github.com/aml-development/ozp-backend/commit/d9e946698ed8a819f35310eb281aedd1ebde96c1))           

### 1.0.40 (2017-02-15)

#### Feature  
* **recommend**:  Ensures Security Filtering of Recommendations ([5386333d](https://github.com/aml-development/ozp-backend/commit/5386333dec92993312af64ae0c62d9b6e82090b5))      

#### Merge Pull Requests  
* Merge pull request #255 from aml-development/recommender_es ([1fc3dafb](https://github.com/aml-development/ozp-backend/commit/1fc3dafbf9cc3ebf2cc723292f71246e923ef337))
* Merge pull request #254 from aml-development/recommender_security ([e1b4509c](https://github.com/aml-development/ozp-backend/commit/e1b4509c6c86e4032c3ec5c18a695b2f5cccd44e))         

#### Changes  
* Folder delete (#256) ([5d8657cc](https://github.com/aml-development/ozp-backend/commit/5d8657ccabfbed6742d333e826b75c793fcda98c))     

### 1.0.39 (2017-02-08)

#### Feature  
* **recommend**:  Added Recommendation Model, Sample Data, Storefront Endpoint ([45d6c232](https://github.com/aml-development/ozp-backend/commit/45d6c2321b9eb955c1b808144b80e334fd1248f0))    

#### Fixes  
* fixed build issues ([ee52b36f](https://github.com/aml-development/ozp-backend/commit/ee52b36fdeb207a59065ab395970a22faaefbf15))
* fixed build issues and added boost values to fields ([6486151b](https://github.com/aml-development/ozp-backend/commit/6486151b62a8732b25e25d4d8ff76174b9e48f62))     

#### Merge Pull Requests  
* Merge pull request #253 from aml-development/recommender ([83539076](https://github.com/aml-development/ozp-backend/commit/83539076266a664b3a2c7f5bd52d650ebcc4608c))         

#### Changes  
* moved comment line to below code line ([5dc68fea](https://github.com/aml-development/ozp-backend/commit/5dc68feaa68d2073ebeed635972c94a722c1e6d5))
* removed commented code ([030a144d](https://github.com/aml-development/ozp-backend/commit/030a144dea4eb8b5c50dae73309549cb6388d28d))
* changed to multi_match and added fuzziness that resolves partial matching issue ([5e528ec1](https://github.com/aml-development/ozp-backend/commit/5e528ec1afeb424ee78327798fe64080d1a3cda5))     

### 1.0.38 (2017-01-25) 

#### Fixes 
* **library**
  *  Added Endpoint for create batch ([1bfd442f](https://github.com/aml-development/ozp-backend/commit/1bfd442ff29c02bd8361764dcdbb9f8707bbbbdf))
  *  Added Access Control Check ([da54c5f2](https://github.com/aml-development/ozp-backend/commit/da54c5f27ca1fad183a17d118f8cf941dd58346f))      

#### Merge Pull Requests  
* Merge pull request #252 from aml-development/251_sharelink ([883baa29](https://github.com/aml-development/ozp-backend/commit/883baa2978a87cc978ce0e4be683d853a0ce3fb9))           

### 1.0.37 (2017-01-19) 

#### Fixes  
* fixing flake formatting issues ([cd8cb669](https://github.com/aml-development/ozp-backend/commit/cd8cb6690a94358186d760184bf78b23485be4ac))     

#### Merge Pull Requests  
* Merge pull request #251 from aml-development/GridChange ([e3a17f6b](https://github.com/aml-development/ozp-backend/commit/e3a17f6b0b7383b909ba81badd9d9e1b5aec1b07))         

#### Changes  
* setting es variable to get build to work ([442c0ce6](https://github.com/aml-development/ozp-backend/commit/442c0ce6af6157f4d54c2d58bed43f9a84e3ddbd))
* added more listing sorting options and set featured to false when listing is deleted ([41e7ff6d](https://github.com/aml-development/ozp-backend/commit/41e7ff6d118e3ae5ae0379c4e180c2e08cec0371))     

### 1.0.36 (2017-01-10)

#### Feature  
* **elasticsearch**:  fixed agency dash search issue ([e579de38](https://github.com/aml-development/ozp-backend/commit/e579de3817296631d29dd21ec4cad0cc85e16826))      

#### Merge Pull Requests  
* Merge pull request #250 from aml-development/pendingdelete ([bab31414](https://github.com/aml-development/ozp-backend/commit/bab314145f762cdd2189de2c583b392e18dbd589))
* Merge pull request #249 from aml-development/es_agency ([fee9de4c](https://github.com/aml-development/ozp-backend/commit/fee9de4c258419549d43be4120b98da140885b0b))
* Merge branch 'GridChange' of github.com:aml-development/ozp-backend into GridChange ([1798374d](https://github.com/aml-development/ozp-backend/commit/1798374d3b627bc9a09fbc352c6f3c20d72d8ea2))
* Merge pull request #248 from aml-development/137_basic_auth ([991e0d50](https://github.com/aml-development/ozp-backend/commit/991e0d506b258b5b0f6cc86f2d68bf0fe7b8fc45))         

#### Changes  
* Update views.py ([56247783](https://github.com/aml-development/ozp-backend/commit/56247783bc3b09e3e8ddcdb3c858958dbd4d9f51))
* Update views.py ([76b0273f](https://github.com/aml-development/ozp-backend/commit/76b0273fb1478935096a041077853df9587dcac2))
* removed app owners form delete listing ([aaa19f1e](https://github.com/aml-development/ozp-backend/commit/aaa19f1e7486b484a0061f3be13884630bde8f67))
* including migrations for pending deletion ([24093955](https://github.com/aml-development/ozp-backend/commit/2409395592ebda9fad43e35db148360eb5db75eb))
* delete listing will now properly allow lisitngs to be deleteted. ([383acf72](https://github.com/aml-development/ozp-backend/commit/383acf722d452b26b9cb7ad7ada92798478a1364))
* changed logic for delete listing where app owners can no longer delete a listing ([67c835cb](https://github.com/aml-development/ozp-backend/commit/67c835cb1e37863b693265a5b9da6896418084b6))
* partially working ([5f95f0b5](https://github.com/aml-development/ozp-backend/commit/5f95f0b5b519d196d87e475fb1b7c57e09f1c5ec))
* owners can now pend a listing for deletion ([8a7608f1](https://github.com/aml-development/ozp-backend/commit/8a7608f14f191b635b6d71d6c4cb98cc85f3f2fe))
* kinda working ([aac66cb0](https://github.com/aml-development/ozp-backend/commit/aac66cb059e4ad4a08f691d5223cc11a76f8513d))
* added sorting by edited_date ([ef52c194](https://github.com/aml-development/ozp-backend/commit/ef52c19453b8421915ee6f60b0172e1d411f51d3))
* added enabled and featured field to ordering ([29f284b5](https://github.com/aml-development/ozp-backend/commit/29f284b5fa23b1044e64d5532477966028a9978f))
* updated  custom ordering ([c8b6d166](https://github.com/aml-development/ozp-backend/commit/c8b6d16681e37d6467e6571a898836e83f2139ee))
* added custom owner ordering logic ([79190ead](https://github.com/aml-development/ozp-backend/commit/79190ead45067d5baa8750684df8a01afc5c360c))
* updated listing endpoint to search and order ([56e4579d](https://github.com/aml-development/ozp-backend/commit/56e4579dd72455f2a1479fc431651c6603b06555))
* added enabled and featured field to ordering ([5b3490c4](https://github.com/aml-development/ozp-backend/commit/5b3490c4ce9f605b7fa6009a5dc89624a70f3072))
* updated  custom ordering ([dab3c528](https://github.com/aml-development/ozp-backend/commit/dab3c528daeae6076e0ae756cbbedda2a6c1a644))
* added custom owner ordering logic ([dd6a8d6f](https://github.com/aml-development/ozp-backend/commit/dd6a8d6f0092b00c467a6cf041dabb7e5f2b19fb))    
* **search**:  Added sorting to search endpoint AML-135 ([34010570](https://github.com/aml-development/ozp-backend/commit/34010570a0e8757f784525f5f031053b9f898a16))     

### 1.0.35 (2016-12-14)

#### Feature  
* **elasticsearch**:  Added support for basic auth ([c4b9d18a](https://github.com/aml-development/ozp-backend/commit/c4b9d18a1e5dbcee79b517fdb6905c6546600ebd))      

#### Merge Pull Requests  
* Merge pull request #247 from aml-development/documentation ([81d2958b](https://github.com/aml-development/ozp-backend/commit/81d2958b7f07fe86654cd931c6a09e14fcab415b))         

#### Changes  
* updated listing endpoint to search and order ([bcbc4c0d](https://github.com/aml-development/ozp-backend/commit/bcbc4c0d52dcbf49a43f6f281fa2c51169da3d19))
* Update README.md ([b5a03615](https://github.com/aml-development/ozp-backend/commit/b5a03615ea35fa97f42a3ee6bb9302c2a13f485c))
* Update README.md ([cc073067](https://github.com/aml-development/ozp-backend/commit/cc073067ee1211454cd350c4a06f60b85893e07e))
* Update README.md ([68e3b36e](https://github.com/aml-development/ozp-backend/commit/68e3b36e75632ab4b629fe5e9a25986fff05108c))    
* **search**:  Added sorting to search endpoint AML-135 ([83e9d716](https://github.com/aml-development/ozp-backend/commit/83e9d716aef4c31e3f26ec74db96167192d403ca))     

### 1.0.34 (2016-12-09)

#### Feature 
* **elasticsearch**
  *  Made reindex more reliable ([72a4196c](https://github.com/aml-development/ozp-backend/commit/72a4196cb277dbe2f30bc3b974b9291c07810223))
  *  Included Launch Url into records ([547c8c62](https://github.com/aml-development/ozp-backend/commit/547c8c62c675d6537fd3f491fd0076ef7ee248f0))
  *  Added Benchmark parser ([830e1c86](https://github.com/aml-development/ozp-backend/commit/830e1c865a7f3c750e0024007cd8ae67fd167b1a))
  *  fixed private apps ([2f61b1da](https://github.com/aml-development/ozp-backend/commit/2f61b1da79f52ef7cf4c8b82618d229539259cbb))
  *  Added id field to suggested results ([39b00865](https://github.com/aml-development/ozp-backend/commit/39b00865ac88d530cdaf19ce2b6a3493f6e0fc27))     

#### Fixes  
* Fixed Elasticsearch previous/next links (#242) ([24878324](https://github.com/aml-development/ozp-backend/commit/24878324c6012d2ee947707dd584549015f49d7f))    
* **listing**:  2pi user storefront was not loading because of owner check. implememted code to fix this ([7b661258](https://github.com/aml-development/ozp-backend/commit/7b661258d6a50790a784eadb73e50ddb90a2d264))     

#### Merge Pull Requests  
* Merge pull request #245 from aml-development/158_es_private_app ([e77b7d8f](https://github.com/aml-development/ozp-backend/commit/e77b7d8f7f5f73a97e4430a39a37c8a7dbcfa08f))
* Merge pull request #246 from aml-development/launch_url_field ([ed61ca34](https://github.com/aml-development/ozp-backend/commit/ed61ca34aa2101985a3147ed5e89c7ac1b37d083))
* Merge pull request #244 from aml-development/2pi_fix ([08193d64](https://github.com/aml-development/ozp-backend/commit/08193d64ea55fede601786b710b360b8a810f089))
* Merge pull request #243 from aml-development/AMLNG-114_suggestObjectUpdate ([93af4122](https://github.com/aml-development/ozp-backend/commit/93af41227c7f4f177cdea9a7c265193bc0142475))           

### 1.0.33 (2016-11-30)

#### Feature 
* **elasticsearch**
  *  refactor and dynamic boost ([321b796d](https://github.com/aml-development/ozp-backend/commit/321b796dd0baf0f76a9f699f14f40ec56c7fddb2))
  *  Made minscore dynamic ([c0d41800](https://github.com/aml-development/ozp-backend/commit/c0d41800b27a56de5c853cc4d561b8d1e5cfec56))       

#### Merge Pull Requests  
* Merge pull request #241 from aml-development/es_boost ([88a273ee](https://github.com/aml-development/ozp-backend/commit/88a273eed214f6d8ddbb280654d40dc407a5adc3))
* Merge pull request #240 from aml-development/es_min_score ([a7d6287b](https://github.com/aml-development/ozp-backend/commit/a7d6287bd3088b46f8a2b8f3d0c45291fa94ca3b))           

### 1.0.32 (2016-11-16)

#### Feature 
* **listing**
  * added skybox listing and pmurt to the lisitng in the build script ([04d8ae2f](https://github.com/aml-development/ozp-backend/commit/04d8ae2f93decf2f18a497d06414f50a11c7e5df))
  * added check for each owners certificate ([4d78553e](https://github.com/aml-development/ozp-backend/commit/4d78553e222c186a864f99744837da45915398b9))     
* **users**: added user to chartcourse for invalid cert testing ([a4c4c5f8](https://github.com/aml-development/ozp-backend/commit/a4c4c5f8692cea13eb44b5f9e5eae7ce0a8bbe15))   
* **elasticsearch**
  *  Refactored search query maker ([3d0949e8](https://github.com/aml-development/ozp-backend/commit/3d0949e85d0efa2ebfc9f370ef0044b450907acf))
  *  Disbled Elasticsearch in Settings for Unit Tests ([493f7578](https://github.com/aml-development/ozp-backend/commit/493f757863a310aca60e2e5e1592b5e107c957c5))
  *  Added Next ([214edb33](https://github.com/aml-development/ozp-backend/commit/214edb335fddb00179e6f5be9acbbbbac6d52e0b))
  *  Added URL to images ([2430a65d](https://github.com/aml-development/ozp-backend/commit/2430a65dd4db050a915aafb31e9016d16384428c))
  *  Changes for Code Review ([60465c52](https://github.com/aml-development/ozp-backend/commit/60465c524e2f0f959e91a373093d497aba6e7abc))
  *  Added Unittest for ElasticsearchUtil ([8165ffa2](https://github.com/aml-development/ozp-backend/commit/8165ffa210329834e57f8957bf00b4c5ffa01dd6))
  *  Code Review Comment Changes ([edd6046d](https://github.com/aml-development/ozp-backend/commit/edd6046d61a2db9611d2175d8f91e62c3f7527ad))
  *  Fixed unit test ([43db4b80](https://github.com/aml-development/ozp-backend/commit/43db4b804cda948268349036458a76ec6f121935))
  *  Added Elasticsearch Library to requirements ([05fb4067](https://github.com/aml-development/ozp-backend/commit/05fb4067cad6cff98845a7dc4032652e725c5952))
  *  Logic for enabling ([68450c27](https://github.com/aml-development/ozp-backend/commit/68450c2732c2f56dedeb4343e8af715997e8dec8))     
* **serilalizers**: added julia to inelegable owners ([f6340624](https://github.com/aml-development/ozp-backend/commit/f6340624e28f9a2b799ae69d8acf0ee77c92e40f))    

#### Fixes  
* **tests**: modified tests to reflect user and application modification ([4a5134b4](https://github.com/aml-development/ozp-backend/commit/4a5134b4e8885253e14a3f0763fa97a591f6fa13))     

#### Merge Pull Requests  
* Merge pull request #237 from aml-development/elasticsearch ([33e60976](https://github.com/aml-development/ozp-backend/commit/33e60976b2a690bd44b598c79b4256fe80bcdb20))
* Merge pull request #239 from aml-development/konsoa_cert ([0f58f7e5](https://github.com/aml-development/ozp-backend/commit/0f58f7e57eeb9639eb27df8a4b8bcc15aafcb957))
* Merge branch 'konsoa_cert' of github.com:aml-development/ozp-backend into konsoa_cert ([0a46256f](https://github.com/aml-development/ozp-backend/commit/0a46256f84063282a730760a9c5fbc86bb837249))         

#### Changes  
* Update requirements.txt ([740658d8](https://github.com/aml-development/ozp-backend/commit/740658d8197c58849b00e53a7d9f142bbb20f7af))
* Update requirements.txt ([76f48691](https://github.com/aml-development/ozp-backend/commit/76f48691ab1f4c1c11a1223f2cf6598c049f6ef6))     

### 1.0.31 (2016-11-07)

#### Feature 
* **elasticsearch**
  *  Added Elasticsearch Util file ([933bd5da](https://github.com/aml-development/ozp-backend/commit/933bd5da3cf6c0356ce2e69d55ad1d274631d7ab))
  *  Refactored Elasticsearch Code ([abcd32ef](https://github.com/aml-development/ozp-backend/commit/abcd32efbce3c1cd07fc4a3eaf228a3cae70d2cd))
  *  Added Logic to modify Elasticsearch Record ([b65b5e3d](https://github.com/aml-development/ozp-backend/commit/b65b5e3d883e378b7f6a19d37ea78215c59f5ef8))
  *  Refactored code and added routes ([baf2a20d](https://github.com/aml-development/ozp-backend/commit/baf2a20d153a8913074cd31f4482f0b957524238))
  *  Added model access file for elasticsearch ([58222069](https://github.com/aml-development/ozp-backend/commit/5822206935d779257ffec34adbe7c08d0257a9d0))
  *  Developed Query String for Search ([23015397](https://github.com/aml-development/ozp-backend/commit/2301539743c03a042ea9569e9358e58831bd4675))
  *  Added script for reindexing ([4f95f176](https://github.com/aml-development/ozp-backend/commit/4f95f176775697e24af81d9dbedc7925cf580726))
  *  Added Learning Python Scripts ([ff518790](https://github.com/aml-development/ozp-backend/commit/ff5187904c3b0d564793fc951f343a626a808a94))       

#### Merge Pull Requests  
* Merge pull request #236 from aml-development/731_ReorderByIsDeleted ([fba7360e](https://github.com/aml-development/ozp-backend/commit/fba7360e8c4fc77e60651d2bb92aee3a7b1d6ddc))         

#### Changes  
* **listing**:  fixed syntax issue #631 ([4034589e](https://github.com/aml-development/ozp-backend/commit/4034589e2ded90f33c76debfb0dbce2ad410240e))    
* **listingmanagement**:  Updated ordering of listings sorted by is deleted then by the edited date. #731 ([63912783](https://github.com/aml-development/ozp-backend/commit/639127830cb4e0dded9623fc2e367b3c2b54591c))     

### 1.0.30 (2016-10-05)

#### Feature 
* **library**
  *  Fixed Logic  #231 ([221bd414](https://github.com/aml-development/ozp-backend/commit/221bd414bb7b1dddcdf3a61022567ed5b2e64225))
  *  Provide support to sort items on HUD #231 ([a50b526e](https://github.com/aml-development/ozp-backend/commit/a50b526e16668eed36f7b62529e768b6d12f8971))     

#### Fixes  
* **autocomplete**:  Fix autocomplete to show enabled ([ff8a3fa1](https://github.com/aml-development/ozp-backend/commit/ff8a3fa1304e6708ba736c2e1ce57a8764d78086))    
* **data**:  made default listing types consistent with customer data and updated unit tests ([ad4917e4](https://github.com/aml-development/ozp-backend/commit/ad4917e4690f06b4c82fbb064d0de042fa8f1b7d))     

#### Merge Pull Requests  
* Merge pull request #232 from aml-development/231_sort_library ([9f3d79c6](https://github.com/aml-development/ozp-backend/commit/9f3d79c64e21ac11de094da7961ef3766a5dfd42))
* Merge pull request #230 from aml-development/229_auto_complete ([acaafd3c](https://github.com/aml-development/ozp-backend/commit/acaafd3ca93b2eee727c5acfd31d72f2cc2cdc6c))
* Merge pull request #228 from aml-development/227_IncreaseTagLength ([5c29a599](https://github.com/aml-development/ozp-backend/commit/5c29a599416ca67184d0ff9144b706bf5b731a97))
* Merge pull request #226 from aml-development/455_newDefaultListingTypes ([21fe9ca3](https://github.com/aml-development/ozp-backend/commit/21fe9ca33161d2c4ef7308403cfab4bec6f473c5))         

#### Changes  
* **tag**:  increase tag length to 30 #227 ([036bd2bd](https://github.com/aml-development/ozp-backend/commit/036bd2bd5690e6ad728e0247fb26d6229f59b576))     

### 1.0.29 (2016-09-21)   

#### Merge Pull Requests  
* Merge pull request #225 from aml-development/chore ([131fbe2a](https://github.com/aml-development/ozp-backend/commit/131fbe2acb4422b91f83e97cfc93917cefa767e8))        

#### Chore 
* **code**
  *  Code clean up 2nd pass ([a8e4aa07](https://github.com/aml-development/ozp-backend/commit/a8e4aa07503a0dbdfad521b826657622b3837703))
  *  Code clean up ([02a170f2](https://github.com/aml-development/ozp-backend/commit/02a170f2b116b00302ca6fdec7e4577271ae5363))       

### 1.0.28 (2016-09-01)

#### Feature 
* **pki**
  *  Ensure pki user can't delete a listing #215 ([9058f1fc](https://github.com/aml-development/ozp-backend/commit/9058f1fc07a8c84206c0ddbddade272a1e892f1a))
  *  Ensure pki user can't submit ([04d27420](https://github.com/aml-development/ozp-backend/commit/04d27420efd1430d09d085386f6ce42739caac67))
  *  Ensure 2PI user are not listing owners #215 ([e6477e13](https://github.com/aml-development/ozp-backend/commit/e6477e1388c4caa719166c376fad8ade27b71a51))
  *  Fixed Unit Tests for Dummy Data #215 ([88d91736](https://github.com/aml-development/ozp-backend/commit/88d917365f9225071cbb28dea49e3ef9bc2b7bb1))
  *  Added PKI users to dummy data #215 ([6b662f42](https://github.com/aml-development/ozp-backend/commit/6b662f42299e873d552666df7925e690a4457c7d))     

#### Fixes  
* **storefront**:  Better error handling ([b29c95c6](https://github.com/aml-development/ozp-backend/commit/b29c95c66768f5ea8ae8f6db4a91cbfc57d3493f))     

#### Merge Pull Requests  
* Merge pull request #222 from aml-development/215_pki ([97fea6e6](https://github.com/aml-development/ozp-backend/commit/97fea6e68fe070ff65947b84e5b3c0b3f1b9e343))
* Merge pull request #220 from aml-development/docs ([7d9fab53](https://github.com/aml-development/ozp-backend/commit/7d9fab533ff8742546f4301d6a4fde61eee8e607))        

#### Chore 
* **docs**
  *  Created entities diagram ascii ([7fd342a4](https://github.com/aml-development/ozp-backend/commit/7fd342a43d43f2cf084dea04009532b1f045b669))
  *  Added PKI Users ([dbc72ad5](https://github.com/aml-development/ozp-backend/commit/dbc72ad58ce7d826800c5d928856c611ce26b29a))     
* **readme**:  Added Ascii Diagram for Submitting a listing ([6e07672e](https://github.com/aml-development/ozp-backend/commit/6e07672ef8d2ed03596fdc4523c7e4908987ba04))    

#### Changes  
* Update ascii-entities.md ([76a4363d](https://github.com/aml-development/ozp-backend/commit/76a4363d60fb73fedfc1641258a83e9755f380f7))
* Update ascii-entities.md ([0c14aa62](https://github.com/aml-development/ozp-backend/commit/0c14aa62b1191159aa97b079b0980b8556b37de9))     

### 1.0.27 (2016-08-26)

#### Feature  
* **pki**:  Add 2dparty Identity #216 ([d997d252](https://github.com/aml-development/ozp-backend/commit/d997d2522b5837d83b8bd97ec9094b9f094d4ec8))      

#### Merge Pull Requests  
* Merge pull request #217 from aml-development/216_2dparty ([53ddd57e](https://github.com/aml-development/ozp-backend/commit/53ddd57eb0e18c5d26b148e4531ca4ccdf79c865))        

#### Chore  
* **readme**:  Added User Info ([ba05adfc](https://github.com/aml-development/ozp-backend/commit/ba05adfc73006cdceab72e717f7b5ba5534675e2))    

#### Changes  
* Update README.md ([447d97d4](https://github.com/aml-development/ozp-backend/commit/447d97d4b2b8d8191e27e7243ca0118037fa2383))     

### 1.0.26 (2016-08-24)

#### Feature  
* **tailorviews**:  Anonymized Data #213 ([a2c3adee](https://github.com/aml-development/ozp-backend/commit/a2c3adee40dcddf2c195a80e4054de44a69b81f4))    

#### Fixes  
* **reviews**:  deletes review is showing wrong user #211 ([3a8c21eb](https://github.com/aml-development/ozp-backend/commit/3a8c21ebb2eff208d4e0340327d45f9adf39982c))     

#### Merge Pull Requests  
* Merge pull request #214 from aml-development/2013_data ([8feab750](https://github.com/aml-development/ozp-backend/commit/8feab750c2f44584428b756a91e19c326425490e))
* Merge pull request #212 from aml-development/211_reviews ([22c730c5](https://github.com/aml-development/ozp-backend/commit/22c730c52d7a76fae9a497c7d39eeb88aaa5fddb))           

### 1.0.25 (2016-08-10)

#### Feature  
* **listing**:  Owners Access Control Check #204 ([2ad4e577](https://github.com/aml-development/ozp-backend/commit/2ad4e577520fb2a9468d8c7087503b77b8713b85))    
* **plugins**:  access control dynamic value #208 ([3512febc](https://github.com/aml-development/ozp-backend/commit/3512febcc506eb658004e8a1e3e727e6f92d965d))      

#### Merge Pull Requests  
* Merge pull request #210 from aml-development/204_listing_updates ([d5d74059](https://github.com/aml-development/ozp-backend/commit/d5d74059b09ffcd749d016873172c7d50d9d1daf))
* Merge pull request #209 from aml-development/208_tailored_views ([89c8c608](https://github.com/aml-development/ozp-backend/commit/89c8c6088693c50a5eb03c14145ca5c7961599e1))           

### 1.0.24 (2016-08-03)

#### Feature 
* **plugins**
  *  Remove Extra Line per Comment #201 ([84e375d9](https://github.com/aml-development/ozp-backend/commit/84e375d9461f9608448f856afb270c6d8957a12c))
  *  Remove Redundant serializer #201 ([37307c46](https://github.com/aml-development/ozp-backend/commit/37307c46feaa926ed5877920227a7f70250b53d1))
  *  Added anonymize_identifiable_data to access_control #201 ([76869d0e](https://github.com/aml-development/ozp-backend/commit/76869d0ec27890ad2e47e62f69db57833dc3306b))     

#### Fixes  
* **endpoints**:  Secure Endpoints #206 ([6249acc2](https://github.com/aml-development/ozp-backend/commit/6249acc27f993c3a6cffe72f7a0ba8abdbabe553))    
* **notification**:  Allow Front-end to dismiss notifications #202 ([ac4348b0](https://github.com/aml-development/ozp-backend/commit/ac4348b0e66a8a5cdb27c9803a8f3fe2364f4237))     

#### Merge Pull Requests  
* Merge pull request #207 from aml-development/permissions ([48adeac6](https://github.com/aml-development/ozp-backend/commit/48adeac660f89bd4fb95a5396aa299e22ca4e91e))
* Merge pull request #205 from aml-development/access_control ([64565846](https://github.com/aml-development/ozp-backend/commit/64565846e906587e86990720c3aa094bebc3ad9d))
* Merge pull request #203 from aml-development/shared_bookmarks ([aaa4ef00](https://github.com/aml-development/ozp-backend/commit/aaa4ef00be81fdbd5880ac1c7f111aec96188bfc))        

#### Chore  
* **readme**:  Updated Travis CI link ([6d321851](https://github.com/aml-development/ozp-backend/commit/6d321851033a9a22976cdee8ba51db1e18588265))      

### 1.0.23 (2016-07-21)

#### Feature  
* **search**:  Added App list to metadata endpoint #192 ([080d88e4](https://github.com/aml-development/ozp-backend/commit/080d88e46ee5c59a818f5f3abfe4edfc77b354c7))      

#### Merge Pull Requests  
* Merge pull request #199 from ozone-development/192_search ([e53c65ff](https://github.com/aml-development/ozp-backend/commit/e53c65ffd8261e0dc12827b24b1c69a141dbd241))
* Merge pull request #196 from ozone-development/error_handling ([a184b977](https://github.com/aml-development/ozp-backend/commit/a184b9779287d4234bb8310a66bf255f316ef88a))
* Merge pull request #198 from ozone-development/shared_bookmark_notifications ([3dc59143](https://github.com/aml-development/ozp-backend/commit/3dc5914326d5426193d14948247db508750e1ee6))        

#### Chore  
* **notification**:  Added more unit test #129 ([8f697f2a](https://github.com/aml-development/ozp-backend/commit/8f697f2a2fc4664809a91cebfa1feefd54ff05f2))   
* **logging**
  *  Added Version to WSGI startup #195 ([b2666dd5](https://github.com/aml-development/ozp-backend/commit/b2666dd5d501639f2e47b74325639625a53337fb))
  *  Import Logging #195 ([03b1522c](https://github.com/aml-development/ozp-backend/commit/03b1522cbf4217e50d0d5704e6a8c0178f6e5e20))       

### 1.0.22 (2016-07-14)

#### Feature  
* **release**:  Hack for msgpack installation ([544d09eb](https://github.com/aml-development/ozp-backend/commit/544d09ebdcbda8e72e63e985088829e2098bdcc8))    

#### Fixes 
* **cache**
  *  Set Timeout variable in plugin manager ([8e4bfb83](https://github.com/aml-development/ozp-backend/commit/8e4bfb83e0406b1f235fb24f2bd2b3b42a1edbed))
  *  Changes for Comment Suggestions ([b6252a4d](https://github.com/aml-development/ozp-backend/commit/b6252a4d85b0ddb45e1532bc6585694f87430702))      

#### Merge Pull Requests  
* Merge pull request #190 from ozone-development/redis_cache ([e56e50b1](https://github.com/aml-development/ozp-backend/commit/e56e50b19731f0c12096f5af3fbd21956a8f58e0))           

### 1.0.21 (2016-06-30)

#### Feature 
* **cache**
  *  Storefront and Metadata Cache  #189 ([803b39f5](https://github.com/aml-development/ozp-backend/commit/803b39f579802942e1e40e4acfdf757d67f9eb2c))
  *  Use Redis for caching #189 ([641ebb10](https://github.com/aml-development/ozp-backend/commit/641ebb10f271fefa6af097ef0c07b8c5c178ef6f))     

#### Fixes 
* **cache**
  *  Clean Code for Access Control Caching ([5a2ab3bf](https://github.com/aml-development/ozp-backend/commit/5a2ab3bf0794f34cd192197c02d88687adbbdabf))
  *  Added redis to travis-ci ([0bf4ab35](https://github.com/aml-development/ozp-backend/commit/0bf4ab350276ed1f80f312fa1af3a3d6d3155632))
  *  Added MessagePack dependency ([1bdfdec8](https://github.com/aml-development/ozp-backend/commit/1bdfdec8d6c350bd859d044822fd3a8f543ebda0))
  *  Fix Unit Tests ([5b5403d8](https://github.com/aml-development/ozp-backend/commit/5b5403d866abe54fcf7c6ebe9c405579cd0f6586))      

#### Merge Pull Requests  
* Merge branch 'master' into redis_cache ([fe8ef088](https://github.com/aml-development/ozp-backend/commit/fe8ef08894da320801fe1d1c84ce652708959b66))
* Merge pull request #188 from ozone-development/20160623_codeclean ([be194b30](https://github.com/aml-development/ozp-backend/commit/be194b309e09a5e68aeea03f971fb8f8ea021d74))        

#### Chore  
* **githooks**:  Added Client-side git hook for commits ([02bd5377](https://github.com/aml-development/ozp-backend/commit/02bd537775d73a390a3149da23495d8168a6bf94))    
* **codeclean**:  Clean and Refactored Code ([f91db4d9](https://github.com/aml-development/ozp-backend/commit/f91db4d9f3ba5866e45a0b707150a163557c1aa4))      

### 1.0.20 (2016-06-22)

#### Feature 
* **notification**
  *  Self Library Import Bookmarks #129 ([ddd7e5f8](https://github.com/aml-development/ozp-backend/commit/ddd7e5f8064ad72f00e2967ccee3a0e766bccbfb))
  *  Self Notification Peer to Peer #129 ([2c510b4b](https://github.com/aml-development/ozp-backend/commit/2c510b4b0d673b2fc1e2f962acfebf6f0d287024))       

#### Merge Pull Requests  
* Merge pull request #187 from ozone-development/129_notification_shared_bookmarks ([75d769aa](https://github.com/aml-development/ozp-backend/commit/75d769aa2bedddb160a39dee694ccda769361784))        

#### Chore 
* **notification**
  *  Fixed dates on TODO Comments #129 ([6235fed4](https://github.com/aml-development/ozp-backend/commit/6235fed48e037fb043c1fe943347060a7cd4a123))
  *  Bookmark Notifications #129 ([c99567f3](https://github.com/aml-development/ozp-backend/commit/c99567f3865508f6130377e7f158c826478faed4))
  *  Notification API unit tests #129 ([4c70e64e](https://github.com/aml-development/ozp-backend/commit/4c70e64ea050f8ffe57952a94a494e0738f4553c))
  *  Refactor code for Bookmark Notification #129 ([43981fdd](https://github.com/aml-development/ozp-backend/commit/43981fddede01ef64665b0f8bce4778c9908e088))       

### 1.0.19 (2016-06-15)

#### Feature  
* **notification**:  Notifications Filtering (All, Pending, Expiring) #184 ([c9c8ecd8](https://github.com/aml-development/ozp-backend/commit/c9c8ecd8adb3b563658a7f1cc1939b2a093da29a))    
* **notifications**:  Stewards Specifying Select Audience #177 ([a3b206b6](https://github.com/aml-development/ozp-backend/commit/a3b206b64419a7a260d0612d0c555b3dd0b9136e))    

#### Fixes 
* **notification**
  *  Merge Conflict ([b988dacd](https://github.com/aml-development/ozp-backend/commit/b988dacd7f828ff376c9417fb7f331758af0b426))
  *  App creators notifying audience (only bookmarked) #176 ([9240663e](https://github.com/aml-development/ozp-backend/commit/9240663e49f2427254cbcf3290858ca543a24fb4))      

#### Merge Pull Requests  
* Merge pull request #183 from ozone-development/177_notification ([1e8e60af](https://github.com/aml-development/ozp-backend/commit/1e8e60afbefb21298441d09ead4969d9784bd1bc))
* Merge branch 'master' into 177_notification ([828a06b3](https://github.com/aml-development/ozp-backend/commit/828a06b3643d10106723ca48a71848d82911d4d0))
* Merge pull request #186 from ozone-development/176_notification_bookmarked ([55ca79f7](https://github.com/aml-development/ozp-backend/commit/55ca79f7e56379246916253badefdb60c6a83558))
* Merge pull request #185 from ozone-development/176_notifications ([65f30781](https://github.com/aml-development/ozp-backend/commit/65f307815791a8fd55b478a6d2fa053c11db4308))           

### 1.0.18 (2016-06-08)

#### Feature  
* **notification**:  App creators Notifying audience #176 ([b5ade746](https://github.com/aml-development/ozp-backend/commit/b5ade746b9ce9dea168cf21b20ee9142e172bfc2))    

#### Fixes  
* **listing**:  Added Search for Listing Tags #170 ([1c8f1c05](https://github.com/aml-development/ozp-backend/commit/1c8f1c05f1bd546a06288764801862ffd25f396c))    
* **tests**: fixed tests to reflect new user additions ([c40f11cd](https://github.com/aml-development/ozp-backend/commit/c40f11cdb3c71cfaea8e576820a7a3c980f39668))     

#### Merge Pull Requests  
* Merge pull request #180 from ozone-development/176_notifications ([8cd06ea2](https://github.com/aml-development/ozp-backend/commit/8cd06ea2c9c139ee903821b259f0ba4a35c48bc1))
* Merge pull request #179 from ozone-development/chore_clean_code ([44656d75](https://github.com/aml-development/ozp-backend/commit/44656d750a27ec3628f336f3f4cc1941da0fa39a))
* Merge pull request #175 from ozone-development/170_search_tags ([82cef713](https://github.com/aml-development/ozp-backend/commit/82cef7133bd67363695c6c244da315c5c736ce7d))
* Merge pull request #172 from ozone-development/wski-newusers ([983a8890](https://github.com/aml-development/ozp-backend/commit/983a88901a201e0a881b8e3a16ef0b218dd53d2c))        

#### Chore 
* **code-cleanup**
  *  Flake8 Code Clean ([40df6305](https://github.com/aml-development/ozp-backend/commit/40df6305486eacca463ac377d8df77c6f012bcd5))
  *  Clean up code for maintainability ([86d94413](https://github.com/aml-development/ozp-backend/commit/86d94413e8c2e1760fc31f41e2caaa562006ec27))     

#### Changes  
* **readme**:  Updated README.md to README.md ([0307854c](https://github.com/aml-development/ozp-backend/commit/0307854c5f7db3d298d3585deab0d1bd07bfa895))    
* Update and rename README.md to chore(readme): Updated README.md ([01f51382](https://github.com/aml-development/ozp-backend/commit/01f513827583d3bc184109ea8b7712a36e84de90))     

### 1.0.17 (2016-06-01)   

#### Merge Pull Requests  
* Merge pull request #174 from ozone-development/autofix/wrapped2_to3_fix ([d8c68bd7](https://github.com/aml-development/ozp-backend/commit/d8c68bd79e1b0b5da2b5e3dc6945340b584d2b3e))         

#### Changes  
* Migrated `%` string formating ([7b8a6b9c](https://github.com/aml-development/ozp-backend/commit/7b8a6b9c1ae8af2e190c4801c8297cadb9f51949))
* Update sample_data_generator.py ([2470fcc6](https://github.com/aml-development/ozp-backend/commit/2470fcc61896c17cf58b4ee9be9b986184c53724))     

### 1.0.16 (2016-05-25)

#### Feature  
* **model_access**:  added a filter to self listings to hide deleted apps ([00f876f3](https://github.com/aml-development/ozp-backend/commit/00f876f3914afc6c5b9adbedf4c23f6224efd9b9))    

#### Fixes  
* **tests**:  added tests for get self listings ([f6735883](https://github.com/aml-development/ozp-backend/commit/f67358839f20038e2ca73642aed6c73f0237dadf))     

#### Merge Pull Requests  
* Merge pull request #171 from ozone-development/169_listing ([c8c80752](https://github.com/aml-development/ozp-backend/commit/c8c8075200a4caba8ad40a6beac6a20900e365bc))           

### 1.0.15 (2016-05-19)

#### Feature 
* **listing**
  *  Users Ability for seeing Recent Activity #167 ([137cba48](https://github.com/aml-development/ozp-backend/commit/137cba4878e55138003f381bbff6762903077858))
  *  Changes for comments #159 ([48ab4a41](https://github.com/aml-development/ozp-backend/commit/48ab4a418238f4bb63c70239b9a9bc12feea1615))
  *  Ability to see if listing is bookmarked #159 ([ce517b7a](https://github.com/aml-development/ozp-backend/commit/ce517b7ae14398eb587aff0e8e94aaa4159e1e15))     
* **notification**:  Sorting Ability for Notifications #160 ([ca5da191](https://github.com/aml-development/ozp-backend/commit/ca5da1913d07a557ecc6814cad69825dc2c119bd))    

#### Fixes  
* **migration**:  Deleted Confliciting Migration File ([79cdfbb0](https://github.com/aml-development/ozp-backend/commit/79cdfbb0576bf4ba3629417d707355d60d8e9f37))    
* **delete_count**:  Add Delete count for listing #163 ([b13a3dd9](https://github.com/aml-development/ozp-backend/commit/b13a3dd9d98584ae5c0fcf09f9f2325975eb3b03))     

#### Merge Pull Requests  
* Merge pull request #168 from ozone-development/167_listing ([273ed02d](https://github.com/aml-development/ozp-backend/commit/273ed02d5d4b92e1eb85abd571d012b3837d0a32))
* Merge pull request #166 from ozone-development/159_listings ([e1d05df9](https://github.com/aml-development/ozp-backend/commit/e1d05df9df93479e12b4b5b4b45992eaa58f0969))
* Merge pull request #165 from ozone-development/160_notifications ([e9a90640](https://github.com/aml-development/ozp-backend/commit/e9a906401892c02f35791891a06c868e624b028e))
* Merge pull request #164 from ozone-development/163_delete_count ([35867bd7](https://github.com/aml-development/ozp-backend/commit/35867bd75cf8249f53e4ca857399d2b22cc2f8c6))
* Merge branch 'master' into 163_delete_count ([55ce4d8c](https://github.com/aml-development/ozp-backend/commit/55ce4d8c2bbff591f1c35e783a20ecb1fb49cc29))
* Merge pull request #161 from ozone-development/plugins ([ff9bbbfc](https://github.com/aml-development/ozp-backend/commit/ff9bbbfcb58555c5d360777085996df851304442))        

#### Chore  
* **release**:   Include the plugin directories in the release ([12d71180](https://github.com/aml-development/ozp-backend/commit/12d71180f2ac67caacca252b81e7a836400f65ec))      

### 1.0.14 (2016-05-12)

#### Feature 
* **plugins**
  *  Added plugin framework typo fix ([623547f2](https://github.com/aml-development/ozp-backend/commit/623547f20f77e6d4e85fd06dee0ef0eb042747d7))
  *  Added plugin framework merge conflicts fixes ([54015826](https://github.com/aml-development/ozp-backend/commit/540158262be0054a3f2c6230f34fbb329fb7c403))
  *  Added plugin framework ([ac3378b4](https://github.com/aml-development/ozp-backend/commit/ac3378b478ef61e6747787621d9bb430aa0ec656))     
* **listing**:  Add Listing DELETED to Activity Log #48 ([e6005387](https://github.com/aml-development/ozp-backend/commit/e60053876a24d787ee26303c40282c7722666a2a))      

#### Merge Pull Requests  
* Merge branch 'master' into plugins ([2f2b2634](https://github.com/aml-development/ozp-backend/commit/2f2b26348a9312806d285139459fa247183f9df5))
* Merge pull request #158 from ozone-development/48_listing_deleted ([789ce895](https://github.com/aml-development/ozp-backend/commit/789ce89587f6487b76d17924136aeef20a9b40b5))        

#### Chore 
* **pep8**
  * Fix Merge Conflicts ([eb775176](https://github.com/aml-development/ozp-backend/commit/eb7751769ae449cae3a0ae1f5b8fba53bf6a9130))
  *  Pep8 Compliance ([ba25d0a8](https://github.com/aml-development/ozp-backend/commit/ba25d0a8f5e02c16994dc8a5e94e2e7ccc10145b))       

### 1.0.13 (2016-04-27) 

#### Fixes 
* **listing**
  *  Add small_icon to support center #156 ([43c8328d](https://github.com/aml-development/ozp-backend/commit/43c8328d031d1d5310ad4f37c31331a7d591390f))
  *  Comment Changes for Classification Validation ([779ad24b](https://github.com/aml-development/ozp-backend/commit/779ad24bce003397890c6bb40255f0b4aee43738))
  *  Added Server Side Validation for Classifications #149 ([cdff3cc5](https://github.com/aml-development/ozp-backend/commit/cdff3cc50704e19f8ee5d83f3446a56240112f19))    
* **library**
  *  Ability to bookmark apps that are enabled only #154 ([83ef7e11](https://github.com/aml-development/ozp-backend/commit/83ef7e11cba5dd9f27649ec327f20e918a9f5f4d))
  *  Getting User's Library now checks listing enabled state #144 ([f9552672](https://github.com/aml-development/ozp-backend/commit/f95526722ebfa817911df2d5ef91ed4c84d76930))     
* **login**:   Allow periods, double-quotes and backtics in usernames. ([867521f6](https://github.com/aml-development/ozp-backend/commit/867521f63f1f98cc7527ddc506244f87f353dc55))   
* **listingactivity**
  *  Made Fixes according to PR Comments ([e2b3660d](https://github.com/aml-development/ozp-backend/commit/e2b3660dc1beda325899380f2b7ebc5ce211ddf8))
  *  Admin tab fixes #141 ([b2e1b410](https://github.com/aml-development/ozp-backend/commit/b2e1b41091f8ca8f41f7f9e7f731d84fb51dcbae))      

#### Merge Pull Requests  
* Merge pull request #155 from ozone-development/154_bookmark_disabled_apps ([46f391ff](https://github.com/aml-development/ozp-backend/commit/46f391ffd14be8fe17699724c0b58704040afd25))
* Merge pull request #157 from ozone-development/156_listing_small_icon ([dfba3800](https://github.com/aml-development/ozp-backend/commit/dfba3800d1a1c667981a3d2444e8d24f0af1c251))
* Merge pull request #153 from ozone-development/login_characters ([fecf167c](https://github.com/aml-development/ozp-backend/commit/fecf167c08493ce097af47ced62d4920def50330))
* Merge branch 'master' into 154_bookmark_disabled_apps ([cefac882](https://github.com/aml-development/ozp-backend/commit/cefac8821dc2fe91bc6f9cad2230580341259ae4))
* Merge pull request #151 from ozone-development/149_listing ([174bfb6b](https://github.com/aml-development/ozp-backend/commit/174bfb6b00eb0f18d10f91c326825a4eabe081e2))
* Merge pull request #148 from ozone-development/chore_unit_test ([abdae6eb](https://github.com/aml-development/ozp-backend/commit/abdae6ebcf4944cbad4c00ca84721044a2fda510))
* Merge pull request #147 from ozone-development/broken_link ([87ed6f2e](https://github.com/aml-development/ozp-backend/commit/87ed6f2e46bf50771377786d27e7bf240f694414))
* Merge pull request #145 from ozone-development/114_library ([df5a793b](https://github.com/aml-development/ozp-backend/commit/df5a793b05285e58d72ec34d0567993d85f59851))
* Merge pull request #142 from ozone-development/141_truncated ([183e03e3](https://github.com/aml-development/ozp-backend/commit/183e03e3e0f7410caf901f46bfd7bca775cdf9a9))        

#### Chore  
* **test**:  Keep important characters in login names ([2a9fb942](https://github.com/aml-development/ozp-backend/commit/2a9fb942552c436bb0065bbf454cb51e7291616f))    
* **unit test**:  Added better tracing for logs ([3e520e3b](https://github.com/aml-development/ozp-backend/commit/3e520e3bfa97b611cf3f572c4a9bee7a4bc35f9b))   
* **unit tests**
  *  Changes for comments PR #148 ([668a5278](https://github.com/aml-development/ozp-backend/commit/668a527896b14e3748976bf655f794d4d1d4bddc))
  *  Profile Tests uses Auth Mock service ([3a624ef1](https://github.com/aml-development/ozp-backend/commit/3a624ef16a7691a0f98ca4478bf072f2f1a0df81))
  *  Created a mock service for authorization ([c646a36a](https://github.com/aml-development/ozp-backend/commit/c646a36ab5bf8e13aa067d37bc286b4315e08c2c))
  *  Unit Tests for Settings and ozp_authorization ([8232a698](https://github.com/aml-development/ozp-backend/commit/8232a698d0c2d15fd77399fe04d960bbd6e38719))     
* **doc**:  Added REST Tracing Docs and how listings get submitted ([f1a667aa](https://github.com/aml-development/ozp-backend/commit/f1a667aaf571cfb38010d1e4a0331b524502366c))    

#### Changes  
* Update README.md ([9eaee983](https://github.com/aml-development/ozp-backend/commit/9eaee98363d22efc9a824aa576f156abe1768634))     

### 1.1.12 (2016-04-13)   

#### Merge Pull Requests  
* Merge pull request #139 from ozone-development/hud_folders ([60d58e39](https://github.com/aml-development/ozp-backend/commit/60d58e39efb34d7d691df7caf287ce4ce29a7299))        

#### Chore 
* **readme**
  *  Added Performance Documentation ([7967c5ab](https://github.com/aml-development/ozp-backend/commit/7967c5ab7244feb7d33612108c36b72c7c83b151))
  *  Performance Debugging with Models ([d832f7da](https://github.com/aml-development/ozp-backend/commit/d832f7daa6f6fcd0540c4ab6fa82c7ba97e49b4d))     
* **documentation**:  API documentation ([5fc1f3a0](https://github.com/aml-development/ozp-backend/commit/5fc1f3a00b2c5a950195ca14062e00ccfb9843d8))    

#### Changes  
* Modified Readme ([8e446421](https://github.com/aml-development/ozp-backend/commit/8e446421d94e16754e17eb026035a8022c16c813))
* Modified Readme ([11e6591a](https://github.com/aml-development/ozp-backend/commit/11e6591a1f13874175f9d022e973f3ba70402502))     

### 1.0.11 (2016-04-05) 

#### Fixes  
* **logging**:  Tune levels of logging for auth service #137 ([71c9e02a](https://github.com/aml-development/ozp-backend/commit/71c9e02afc255aa7aceaf23703e01209ab77693a))    
* **search**:  Made sure the correct listing are showing in search #135 ([bca24a8c](https://github.com/aml-development/ozp-backend/commit/bca24a8c32236cfcd3541271df76297cc0646111))     

#### Merge Pull Requests  
* Merge pull request #138 from ozone-development/rivera_logging_tuning ([676cff72](https://github.com/aml-development/ozp-backend/commit/676cff723926a83164d4dd9b8e36d146bd67056f))
* Merge pull request #136 from ozone-development/fix_search_135 ([2b6cb607](https://github.com/aml-development/ozp-backend/commit/2b6cb607d2f168584925b8471d2541dc7d3ee10c))           

### 1.0.10 (2016-03-30)

#### Feature 
* **profile**
  *  Corrected Logic to get Listing for a Profile ([fc33d5eb](https://github.com/aml-development/ozp-backend/commit/fc33d5eb9b8c8a430f2215512e3794aa0b64b2e6))
  *  Unit tests for getting Listings for Profiles ([214284ec](https://github.com/aml-development/ozp-backend/commit/214284ec1d358554e280537e6cc05c91415169b4))
  *  Get listing for profiles access control ([7e7b4697](https://github.com/aml-development/ozp-backend/commit/7e7b4697979e6b5bb14e21eaebab229e1d0a1aad))
  *  Get Listings for Profiles ([28c68f76](https://github.com/aml-development/ozp-backend/commit/28c68f7673d2c0521a021974d13cd47714d8341a))     

#### Fixes  
* **profile**:  Return stewards sorted by display name ([82680170](https://github.com/aml-development/ozp-backend/commit/8268017044cbdeac5d805daf7936905dfef61302))     

#### Merge Pull Requests  
* Merge pull request #134 from ozone-development/profile_listings ([f5decee2](https://github.com/aml-development/ozp-backend/commit/f5decee209b9fafe361d772f77dc5d802b0cde5f))
* Merge branch 'master' into profile_listings ([c82948b2](https://github.com/aml-development/ozp-backend/commit/c82948b2a095b2e4bf97320a0980a9f5e81527e5))
* Merge pull request #133 from ozone-development/sorted_stewards ([77811e99](https://github.com/aml-development/ozp-backend/commit/77811e99b41f38707cfcffd7589926385e6ef781))         

#### Changes  
* remove logging ([6d1d2b4c](https://github.com/aml-development/ozp-backend/commit/6d1d2b4c8c9bb10d580f0c575b6625c83d7b9c65))
* remove logging ([a8135f14](https://github.com/aml-development/ozp-backend/commit/a8135f14aaafc539ed8a649934281c1e7d53bebc))     

### 1.0.9 (2016-03-23) 

#### Fixes  
* **dn**:  We should keep the dashes in user's DNs ([e5f36e8b](https://github.com/aml-development/ozp-backend/commit/e5f36e8b1bfac168733f35d32b38de79c2f18662))    
* **create/edit page**:  Changing the security marking ([cfe7f315](https://github.com/aml-development/ozp-backend/commit/cfe7f31574c7c03edbe707c94c9756056fb01cd9))     

#### Merge Pull Requests  
* Merge pull request #128 from ozone-development/dn_dashes ([a800470d](https://github.com/aml-development/ozp-backend/commit/a800470d3b35bc001346bba96cfb1493335b39a5))
* Merge pull request #127 from ozone-development/listing_123 ([f1283bfd](https://github.com/aml-development/ozp-backend/commit/f1283bfd995155cd32ba90cdd68a998c50dba026))           

### 1.0.8 (2016-03-22) 

#### Fixes 
* **notification**
  *  Removed un-used 'Dismissed By' key from serializer ([0b529717](https://github.com/aml-development/ozp-backend/commit/0b529717faf7d7c511ba0104a61bc7bbaeb2a5e2))
  *  Fixed Delete Authorization ([e3e2706b](https://github.com/aml-development/ozp-backend/commit/e3e2706b35b8b288a212b997d9add8c9fa259d70))     
* **listing**:  Don't duplicate contacts in db on listing create ([619ec860](https://github.com/aml-development/ozp-backend/commit/619ec860a39b30db187ce8678b7c350c2a932c47))     

#### Merge Pull Requests  
* Merge pull request #124 from ozone-development/imagesize ([0b1ab296](https://github.com/aml-development/ozp-backend/commit/0b1ab2968fe3a4641246a095a30252930dffe95e))
* Merge pull request #125 from ozone-development/contacts_create ([dfdb5c67](https://github.com/aml-development/ozp-backend/commit/dfdb5c67a8bfbdc3a684309d7815c81d2cd58c32))
* Merge pull request #126 from ozone-development/notification ([8a968bc4](https://github.com/aml-development/ozp-backend/commit/8a968bc4eeeb498e76177fd1798aa925402f6a47))         

#### Changes  
* Ugly fix for image size check issue ([637ef119](https://github.com/aml-development/ozp-backend/commit/637ef119d5026e8325457b8c1383a0622a26411e))     

### 1.0.7 (2016-03-21) 

#### Fixes  
* **submit listing**:  Changing Contact Fields Saves ([80e3543d](https://github.com/aml-development/ozp-backend/commit/80e3543dbf5533bceb63ff4c4b8d4254b2193e72))    
* **quickview**:  Storefront call should return owner display name ([b2a5ca29](https://github.com/aml-development/ozp-backend/commit/b2a5ca291e8a93aee0ad7936a156b951ee56faba))     

#### Merge Pull Requests  
* Merge pull request #121 from ozone-development/118_sumbit_listing ([2826cf2c](https://github.com/aml-development/ozp-backend/commit/2826cf2c7a70e7af747ca702aa785ba7880dbd05))
* Merge pull request #120 from ozone-development/storefront_owner ([c10c8176](https://github.com/aml-development/ozp-backend/commit/c10c817655b04f001b4f8ae59e400877f140568a))           

### 1.0.6 (2016-03-20)

#### Feature  
* **json_logging**:  Logs Formatted as JSON ([6c95c5c0](https://github.com/aml-development/ozp-backend/commit/6c95c5c062bbaaa5abf845d7e439a1aa3354ebe9))    

#### Fixes 
* **makefile**
  *  restart_clean_dev_server.sh no longer exists ([da4243cd](https://github.com/aml-development/ozp-backend/commit/da4243cd6a6ad475cf125951648ea3aac4dca570))
  *  restart_clean_dev_server.sh no longer exists ([513b1162](https://github.com/aml-development/ozp-backend/commit/513b1162057723cb0e868f234d4c7ea1fed69be4))     
* **listing**:  Simple fixes for listing order in 'search' and 'new arrivals' ([3aa14616](https://github.com/aml-development/ozp-backend/commit/3aa14616da47ef8e0888d7c8042cff51d4478624))    
* **library**:  Allow API call to retrieve all listing that have a Listing type  ([1d235ea9](https://github.com/aml-development/ozp-backend/commit/1d235ea92e75502094528f42187795757662e071))    
* **categories**:  Categories shown in sorted order ([485a984b](https://github.com/aml-development/ozp-backend/commit/485a984b677e5693bc6968a0acccd5719f1d5c70))    
* **portion marking**:  For this release portion markings are informational only ([6d139bea](https://github.com/aml-development/ozp-backend/commit/6d139beac1e4cd51b426d0fe5f0cf5baea3945d9))     

#### Merge Pull Requests  
* Merge pull request #116 from ozone-development/listing_order ([916cd6c7](https://github.com/aml-development/ozp-backend/commit/916cd6c761371661f01878d9efc58701a53c42f2))
* Merge pull request #117 from ozone-development/makefile ([d0e709a5](https://github.com/aml-development/ozp-backend/commit/d0e709a592f50a30b1afdb8c7e5c09485eaf606d))
* Merge pull request #114 from ozone-development/self_listing_type_filter ([3c85324d](https://github.com/aml-development/ozp-backend/commit/3c85324d6e67223c35a6f529530967b5628f0b54))
* Merge pull request #108 from ozone-development/makefile ([6985d9be](https://github.com/aml-development/ozp-backend/commit/6985d9be8d8fb9f3de1ab735548c9ef949ae7371))
* Merge pull request #110 from ozone-development/informational_markings ([532fbf42](https://github.com/aml-development/ozp-backend/commit/532fbf4210f6c2a6c1dfc92c24c9ffc005f8ed97))
* Merge pull request #112 from ozone-development/category_order ([8d024e19](https://github.com/aml-development/ozp-backend/commit/8d024e191b826dbeef8435adc35f97feec8d8327))
* Merge pull request #107 from ozone-development/json_logging ([34730bc9](https://github.com/aml-development/ozp-backend/commit/34730bc90f0ef2671c90f1b956971f3cccf5c6d4))        

#### Chore  
* **makefile**:  Replaced script files with one Makefile ([f32a723c](https://github.com/aml-development/ozp-backend/commit/f32a723cbd2404fb2a7266dce74312521372d327))    

#### Changes  
* update tests ([bdb55602](https://github.com/aml-development/ozp-backend/commit/bdb5560284cf13020263540fd2fab7514af746b0))     

### 1.0.5 (2016-03-16)

#### Feature 
* **tour new user flag**
  *  Fixed Variable Naming for Tests ([d376b214](https://github.com/aml-development/ozp-backend/commit/d376b2145b5f33a3b9316a1575c79358e379342d))
  *  Checked in compatible migration files for master branch ([6d0cc878](https://github.com/aml-development/ozp-backend/commit/6d0cc878d458abeac68585ece716c09cf0e45ee3))     

#### Fixes  
* fix tests broken by multiple copies of listings ([75e26b0b](https://github.com/aml-development/ozp-backend/commit/75e26b0b1f910d40040c422044357b896d7c31ff))   
* **auth**
  *  Add test for mixed case DNs ([d4645bc1](https://github.com/aml-development/ozp-backend/commit/d4645bc18136be897cb289bd5d5d9cfc2f01cc37))
  *  Allow a default agency for those users in an agency without an Org Steward ([bca25835](https://github.com/aml-development/ozp-backend/commit/bca25835650705371f25d06675b8468339783795))
  *  Treat usernames as case-insensitive #96 ([14fe3302](https://github.com/aml-development/ozp-backend/commit/14fe3302fc88f577efeb5f2c5106225dded92f2b))      

#### Merge Pull Requests  
* Merge pull request #103 from ozone-development/agency ([8c1187f5](https://github.com/aml-development/ozp-backend/commit/8c1187f5b9ac05b4eb5535f31d6479c79f29e805))
* Merge pull request #100 from ozone-development/caseinsensitive-user ([e0ffc2f7](https://github.com/aml-development/ozp-backend/commit/e0ffc2f7bf85524dd7d4940e54406677b03e7517))
* Merge pull request #104 from ozone-development/wski-patch-1 ([7256aa27](https://github.com/aml-development/ozp-backend/commit/7256aa27891bdb83c4c79fb8c1ddcd7553a2f871))
* Merge pull request #82 from ozone-development/eriver-development ([93364aef](https://github.com/aml-development/ozp-backend/commit/93364aef3fb3caa9756a22928c66493d5c03594d))        

#### Chore  
* **sample data**:  10x the sample listings. ([262c1aaf](https://github.com/aml-development/ozp-backend/commit/262c1aaf7424e701e83ea802451c16d2789b5d63))      

### 1.0.4 (2016-03-09)

#### Feature 
* **tour new user flag**
  *  Added Boolean Tour Flags for ozpcenter, webtop, hud ([a7741f8e](https://github.com/aml-development/ozp-backend/commit/a7741f8e1e2ab5d0cf0e89dbaa176ecbc5495e90))
  *  Pull Request Comments Fixes Continuation ([95826484](https://github.com/aml-development/ozp-backend/commit/958264847b0efb7a3d5566c410c57cf416ad453a))
  *  Pull Request Comments Fixes Continuation ([5437124f](https://github.com/aml-development/ozp-backend/commit/5437124fc18c06034093cd35dbab7061261eb0a9))
  *  Pull Request Comments Fixes ([18ad27bb](https://github.com/aml-development/ozp-backend/commit/18ad27bbd1c14ffdadb8197ad90b4efe41e6d6a5))     

#### Fixes  
* **speed**:  prefetch storefront data for speed improvements ([7bf807ca](https://github.com/aml-development/ozp-backend/commit/7bf807ca408d4c8c4c54d1f409845e16fa38a5e2))     

#### Merge Pull Requests  
* Merge pull request #89 from ozone-development/clark_temp ([7ee8ab99](https://github.com/aml-development/ozp-backend/commit/7ee8ab995a91ee3bce311870aafc6f319c073a70))
* Merge branch 'master' into eriver-development ([ef065892](https://github.com/aml-development/ozp-backend/commit/ef0658927feae86041f7838878d125152453051d))
* Merge pull request #87 from ozone-development/86_travisci ([33281b2b](https://github.com/aml-development/ozp-backend/commit/33281b2b7f8712eea1091e50b8ffb9ab9b52208b))
* Merge branch 'master' into eriver-development ([e946fa1d](https://github.com/aml-development/ozp-backend/commit/e946fa1d89f3ac93840dd76d04e92cb53ad46eb9))
* Merge pull request #84 from ozone-development/pep8 ([9866b2e8](https://github.com/aml-development/ozp-backend/commit/9866b2e84a734eb160c137f70d328cce677b3504))        

#### Chore  
* **travisci**:  Include Travis-CI so that the build fails if a unit test fail ([e09cda6f](https://github.com/aml-development/ozp-backend/commit/e09cda6fe029ab0a80d732bdd726f5719f06314e))    
* **pep8**:  Make the Backend Python PEP8 compliant and provide Unit Test Code Coverage ([8ebbf668](https://github.com/aml-development/ozp-backend/commit/8ebbf6681f5f9bf013dd472ba3b00bb0f4e029be))    

#### Changes  
* Update .travis.yml ([ce1f8862](https://github.com/aml-development/ozp-backend/commit/ce1f8862b4e72e266e6bceb156714e99ca5ed77d))
* Update settings.py ([d98d8c27](https://github.com/aml-development/ozp-backend/commit/d98d8c27df1c97960f51ccb0a1c1b4ff08e53821))     

### 1.0.3 (2016-03-03)

#### Feature  
* **tour new user flag**:  Added support for Tour New User Flag and Added Migration Scripts #81 ([d935d756](https://github.com/aml-development/ozp-backend/commit/d935d756dd13d20d57e86e2bae2116af87510a7b))    

#### Fixes 
* **pkiauth.py**
  *  Update username generation to match db migration script ([7f4f5843](https://github.com/aml-development/ozp-backend/commit/7f4f58430aa84c0a04b38106bd707e8ca4886e32))
  *  Limit new user's usernames to 30 chars or less ([fcaa47ab](https://github.com/aml-development/ozp-backend/commit/fcaa47ab27a70655bccace58de28e50a738bf259))     
* **auth**:  Reverse DNs received from nginx ([c145a0b7](https://github.com/aml-development/ozp-backend/commit/c145a0b7667cabb864a33998392473965e3eb726))    
* **models.py**:  Give org stewards access to the correct set of listings ([9a963b1f](https://github.com/aml-development/ozp-backend/commit/9a963b1fa7e20b66e9455a2394d2504cd6b682f4))     

#### Merge Pull Requests  
* Merge pull request #79 from ozone-development/issue-77-create-user-fails ([5e2c1c5c](https://github.com/aml-development/ozp-backend/commit/5e2c1c5c4ac2fefe734a5a741a2f187e5ec49f5e))
* Merge pull request #80 from ozone-development/issue-78-better-dn-check ([d255ca3c](https://github.com/aml-development/ozp-backend/commit/d255ca3c7c67bf71a3f732cb5768239c3b05701a))
* Merge pull request #76 from ozone-development/fix-sample-user-logins ([38bd3f0b](https://github.com/aml-development/ozp-backend/commit/38bd3f0bd64ce5d32cd9a50fdf0410ca604b3992))
* Merge pull request #75 from ozone-development/issue-74-org-steward-access ([41819a72](https://github.com/aml-development/ozp-backend/commit/41819a72a645eea45142090f84f8df14e937be6f))        

#### Chore  
* **sample data**:  Update DNs for sample data users so they work with ([0f9e1fa4](https://github.com/aml-development/ozp-backend/commit/0f9e1fa4123a75ac4b478ba5a8949e8e6a4524e9))    

#### Changes  
* Mark point in file where we need to reverse the user and issuer DNs ([695f38df](https://github.com/aml-development/ozp-backend/commit/695f38df1abaae31c991d49b85e4b41851b2132f))
* relase-1.0.2 ([45edeaa4](https://github.com/aml-development/ozp-backend/commit/45edeaa458d2aa1abd25d88507b5d4fcd63ec0b1))     

### 1.0.1 (2016-02-10)         

#### Changes  
* update settings.py to fix python manage.py flush issue ([c5f5c792](https://github.com/aml-development/ozp-backend/commit/c5f5c79250fa4b915bdfde494455ba80782458d1))
* (feat) added contributing file ([01048357](https://github.com/aml-development/ozp-backend/commit/010483576c2f047074d596ae5dc84f268f0ae16e))     

### 1.0.0 (2016-01-27)         

#### Changes  
* python backend is merged in master now ([fe9f2df9](https://github.com/aml-development/ozp-backend/commit/fe9f2df952c7b668c7be72201e858649ce4acf05))
* update release script to support pip 8.0.0 (changed default wheel dir) ([c14027cc](https://github.com/aml-development/ozp-backend/commit/c14027cc630cf4ac51248dc246562df5b6f0eed4))
* remove old package from setup.py ([da5f626c](https://github.com/aml-development/ozp-backend/commit/da5f626c3b5b09f6eb3c660d19aa12c8961e8123))     

### 0.9.9 (2016-01-19)         

#### Changes  
* add additional checks for security markings ([391785d9](https://github.com/aml-development/ozp-backend/commit/391785d9704cd8dac1da08547d39b7155a99cc05))     

### 0.9.8 (2016-01-13)         

#### Changes  
* add security_marking validation for images ([5605198a](https://github.com/aml-development/ozp-backend/commit/5605198a642d627872f65bc816ecb1f0167de38b))
* give better response if security_marking is invalid ([2cd70081](https://github.com/aml-development/ozp-backend/commit/2cd70081d560a886950136ee404483ce35c06e07))
* validation on security marking when submitting or editing a listing ([64dbfcf7](https://github.com/aml-development/ozp-backend/commit/64dbfcf774f026822b7b8441a9f8db44ae85d35f))     

### 0.9.7 (2016-01-06)         

#### Changes  
* allow listings to be assigned to any valid agency ([1e2669ba](https://github.com/aml-development/ozp-backend/commit/1e2669ba5a3ba79f49887cc11310d9cf4dc973fc))
* support searching profiles by dn ([0bdbd27a](https://github.com/aml-development/ozp-backend/commit/0bdbd27a57cbf0e9481065106fb8f8cf66808d47))
* remove custom pagination for Listing Reviews ([a8b0c7aa](https://github.com/aml-development/ozp-backend/commit/a8b0c7aa311ef2d03a30a891c9cd825c3514b0cf))
* update pagination and fix bug in library endpoint ([10b89343](https://github.com/aml-development/ozp-backend/commit/10b8934348f10858e690899be361130969e5b4c7))     

### 0.9.6 (2015-12-18)         

#### Changes  
* increase max size of Listing.description field. update readme. support update of Listing.security_marking ([2a83bac0](https://github.com/aml-development/ozp-backend/commit/2a83bac0a56fddad83886b53699d4612e02f9027))
* increase size of access_control field ([044ab3fb](https://github.com/aml-development/ozp-backend/commit/044ab3fb68b81a1181828a7480fd950d028dc2b8))
* dont hide private listings from apps mall stewards ([9961a136](https://github.com/aml-development/ozp-backend/commit/9961a1361b580fc8111160462fe80b3e9c592870))
* don't overwrite security_marking ([b1b1ebdd](https://github.com/aml-development/ozp-backend/commit/b1b1ebdd93701ed8a1827cd71974f9fb2565d4c0))
* updates ([818d365d](https://github.com/aml-development/ozp-backend/commit/818d365d92387b96dcf4ce20ceaaccbae9d19f60))
* adding location apps to sample data ([56545097](https://github.com/aml-development/ozp-backend/commit/56545097576e3ea59b1427807459898a2ec7cee2))
* add support for configurable demo root ([617286c3](https://github.com/aml-development/ozp-backend/commit/617286c3f22bca32a703dc83d7a5791e9418b0c7))
* ozp authorization update ([ebaf5aa6](https://github.com/aml-development/ozp-backend/commit/ebaf5aa6ac437f94f6ba03a936b371bcf2ff8799))
* update to pki auth ([dd2e17f7](https://github.com/aml-development/ozp-backend/commit/dd2e17f761a7d0fbd1efcf949d6fee2e961314df))     

### 0.9.5 (2015-11-25)         

#### Changes  
* add comment ([071e0894](https://github.com/aml-development/ozp-backend/commit/071e0894a6caf89b760e5d70d441b89995c3c3c5))
* add log ([11303fb9](https://github.com/aml-development/ozp-backend/commit/11303fb995ed5736674745e8c446c37f81a4cd3c))
* updates to pkiauth ([3dbde10b](https://github.com/aml-development/ozp-backend/commit/3dbde10b697180363848ff7a9785b0da60e7673f))
* make dn separator configurable ([3156069d](https://github.com/aml-development/ozp-backend/commit/3156069d15e753a84377dd8403a340b3dcaf137d))
* remove demoauth ([501f9306](https://github.com/aml-development/ozp-backend/commit/501f9306d399164f8486eea2cb1d9aef64326b50))
* remove demoauth from release script ([39ee2a84](https://github.com/aml-development/ozp-backend/commit/39ee2a84c84f3a521a676a61bd8c1d6298c54039))
* moved demoauth into its own repo ([60b303b3](https://github.com/aml-development/ozp-backend/commit/60b303b3a513d20b3b10aac41a59210d55d18abd))     

### 0.9.4 (2015-11-18)         

#### Changes  
* update to demo auth server urls and db migration script ([627720f6](https://github.com/aml-development/ozp-backend/commit/627720f6c10e2b958ac24ceee8c048e6ad185aef))
* first pass of db migration script complete ([2997dfa3](https://github.com/aml-development/ozp-backend/commit/2997dfa31595636ca8e10ea48dcb1eef1d6768f1))
* db migration update ([28f659d0](https://github.com/aml-development/ozp-backend/commit/28f659d0d5a82c29f70ddb7fab9c709273a6a381))
* db migration update ([c4da3609](https://github.com/aml-development/ozp-backend/commit/c4da36097153b66f8b9049b3dc90bbb8191cfea3))
* db migration update ([e5f1b11f](https://github.com/aml-development/ozp-backend/commit/e5f1b11f85f2d64fa00152347d6552500f0facfd))
* db migration updates ([14337d7b](https://github.com/aml-development/ozp-backend/commit/14337d7bb6ef08cda7d6a44b39aa346851fb89b2))
* db migration update ([e32b467e](https://github.com/aml-development/ozp-backend/commit/e32b467e774e5ea2a79208aa217b12154f4dba4b))
* updates for db migration ([4bfd62bf](https://github.com/aml-development/ozp-backend/commit/4bfd62bf2e5f49769bd17169787795d048d9635f))
* pki auth - update issuer dn for existing profiles ([df8d4932](https://github.com/aml-development/ozp-backend/commit/df8d4932516c723e55da907358aca7b2632ae689))
* update db migration script for hex values ([a8f4abac](https://github.com/aml-development/ozp-backend/commit/a8f4abac4caf8a1091ca77384e5c7d0ae7085823))
* add onetime db migration script ([adcd9cbc](https://github.com/aml-development/ozp-backend/commit/adcd9cbc737a24845457ec9f83dc5b359213c657))
* auth update url ([5af5ea35](https://github.com/aml-development/ozp-backend/commit/5af5ea35314bd00803c896869656cd8962f26f6f))
* update auth to use issuer dn and change singleton to iframe_compatible ([db20a21b](https://github.com/aml-development/ozp-backend/commit/db20a21b3f97d21d64c33d4bbe87ddbd8c45b5ac))
* add sql script to create db ([03a19b36](https://github.com/aml-development/ozp-backend/commit/03a19b36cfbd5b0b590d63247b4edb9734a26596))     

### 0.9.3 (2015-11-11) 

#### Fixes  
* fix auth url ([834ab33a](https://github.com/aml-development/ozp-backend/commit/834ab33aabba763b6d5ff07b3d24767f3700b2dd))
* fixed unit tests, OzpAuthorization working ([5cd05d03](https://github.com/aml-development/ozp-backend/commit/5cd05d0393c25e966354fa169a0aee9a7b72dcc3))
* fix optional phone numbers for contacts ([ec56d73e](https://github.com/aml-development/ozp-backend/commit/ec56d73ed3477d15481e0e2fb74c09442def22ae))      

#### Documentation  
* doc and url updates ([2bfaf75a](https://github.com/aml-development/ozp-backend/commit/2bfaf75ab647f7098da79dc6f230e8178604fbdc))        

#### Changes  
* update settings ([ffc77ed4](https://github.com/aml-development/ozp-backend/commit/ffc77ed467147aee91e6b2761b291c5e6e9040f6))
* update logging settings. fix pkiauth. ([c03eb384](https://github.com/aml-development/ozp-backend/commit/c03eb38419875122cbee276a225b982652f0ba1a))
* finish removal of models.AccessControl ([2a2c5cbf](https://github.com/aml-development/ozp-backend/commit/2a2c5cbf7400209048e978c0f08332926b5ecb00))
* auth updates ([6e8708c4](https://github.com/aml-development/ozp-backend/commit/6e8708c44311340b77000a67063084cee6d12778))
* updated authorization to be more inline with the actual service ([ada2b0ee](https://github.com/aml-development/ozp-backend/commit/ada2b0ee7b18b1f4f629a8035223afdedafbfcfb))
* changed authorization scheme ([dffa44a4](https://github.com/aml-development/ozp-backend/commit/dffa44a48ce388218bf30f6fd18733ab08f38a35))
* cleanup ([5b70a7a2](https://github.com/aml-development/ozp-backend/commit/5b70a7a257db8117bbe2354de6a6036584ca0c90))
* authorization updates ([2d0bd1e5](https://github.com/aml-development/ozp-backend/commit/2d0bd1e5857c906e9de9619783c5a88e1a120ea1))
* make phone numbers optional for contacts ([77a32ebf](https://github.com/aml-development/ozp-backend/commit/77a32ebfae54e7185560c394ae5ce9042500ce6e))
* contact.secure_phone and contact.unsecure_phone should be optional ([96f7683f](https://github.com/aml-development/ozp-backend/commit/96f7683f41985b3a3372112f618ca90a44cedf48))     

### 0.9.2 (2015-11-04) 

#### Fixes  
* **iwc**:  application template pattern needs trailing fslash ([b7152dd4](https://github.com/aml-development/ozp-backend/commit/b7152dd4f36af10f128aebb86b97afa727adb745))    
* fixing broken unit tests ([1f972f56](https://github.com/aml-development/ozp-backend/commit/1f972f56817a7a257b0d84eccfbad37605546e9a))           

#### Changes  
* update release script to include demoauth module ([e38a4531](https://github.com/aml-development/ozp-backend/commit/e38a4531d53bb367b1a3e641235566dd5b67a189))
* demoauth service updates ([43bf58de](https://github.com/aml-development/ozp-backend/commit/43bf58de41a493dd2f07d02c88bf2cd23daea0d8))
* adding demoauth authorization service ([b4fb0930](https://github.com/aml-development/ozp-backend/commit/b4fb09301165e98108fe55147740a4755f73f33f))
* BaseAuthorization tests ([10456e59](https://github.com/aml-development/ozp-backend/commit/10456e591edcb2b3ad385f3a2dd4ee6f31ae3d42))
* adds tests for pki auth ([ad4c5b74](https://github.com/aml-development/ozp-backend/commit/ad4c5b74a457395cfbbce819ddb514c4316c2341))
* auth updates ([d931988e](https://github.com/aml-development/ozp-backend/commit/d931988e4ec5eee3766e03e4f8962a7d48f97393))
* update iwc root response ([b2a3624b](https://github.com/aml-development/ozp-backend/commit/b2a3624bfa3e3034d24f76b39ad177a2b498b6f3))
* add ozp:data-item and ozp:application-item to root iwc endpoint ([55bda4b3](https://github.com/aml-development/ozp-backend/commit/55bda4b36bdde4b389e9e09b3842fdb66c66751e))
* return all data in the ozp:data-objects endpoint ([cc90a515](https://github.com/aml-development/ozp-backend/commit/cc90a5152c67cea7bb810b1671527723934d1d2a))
* adding application data to _embedded for ozp:application endpoint ([e6398dd7](https://github.com/aml-development/ozp-backend/commit/e6398dd76b10b0233138c859e1437b37f7ce8771))     

### 0.9.1 (2015-10-28)         

#### Changes  
* remove 'collection' from iwc data ([bc880517](https://github.com/aml-development/ozp-backend/commit/bc880517720ee0abea1132b8df4262afefa7e3f8))
* use correct media_type for iwc data objects ([214cf0d7](https://github.com/aml-development/ozp-backend/commit/214cf0d7521633adfd0df6c8bcaedcba02062c6c))
* added type with all hrefs for iwc api ([b1cd67df](https://github.com/aml-development/ozp-backend/commit/b1cd67dff9891788dec434e0bd7f128ea4ececaa))
* add support for custom content negotiation for iwc endpoints ([5456e851](https://github.com/aml-development/ozp-backend/commit/5456e8516ff91efd58a415d5ce816ffa3e156fc3))
* sort listing activities by reverse chron order ([2e0ae2f8](https://github.com/aml-development/ozp-backend/commit/2e0ae2f8edd0ffdb23729f6eb9030170822508e9))
* add edited_date to listing reviews ([722ecaa1](https://github.com/aml-development/ozp-backend/commit/722ecaa125229dac77369f32b58b13b648b72f86))     
 