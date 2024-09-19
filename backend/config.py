import os

KG_FILE = "knowledge/concat_first_second_other_data_20231227_text.pkl"

# OpenAI
KEY_FILE = os.getenv("OPENAI_KEY_FILE", "key.txt")
EMB_NAME = os.getenv("OPENAI_EMB_NAME", "text-embedding-3-large")
#  text-embedding-3-large
LLM_NAME = os.getenv("OPENAI_LLM_NAME", "gpt-4o")
# LLM_NAME = os.getenv("OPENAI_LLM_NAME", 'Llama3-Taiwan-70b-Instruct-q5_k_m.gguf:latest')

# "Llama3-Taiwan-70b-instruct-q5_k_m.gguf:latest"
# "gpt-4o"
DB_FILENAME = ['勞工職業災害保險給付後限期投保單位繳納辦法',
 '事業單位優先僱用經其大量解僱失業勞工獎勵辦法',
 '船舶清艙解體職業安全規則',
 '取得華僑身分香港澳門居民工作許可審查收費標準',
 '事業機構支付職業訓練費用審核辦法',
 '勞工志願服務獎勵辦法',
 '不當勞動行為裁決委員案件審理給付報酬標準',
 '鉛中毒預防規則',
 '勞動部勞動基金監理會設置辦法',
 '林場安全衛生設施規則',
 '產品安全資訊申報登錄及型式驗證規費收費標準',
 '地方主管機關受理工作場所性騷擾事件申訴處理辦法',
 '優先管理化學品之指定及運作管理辦法',
 '營造安全衛生設施標準',
 '升降機安全檢查構造標準',
 '勞工保險失能給付標準',
 '受聘僱從事就業服務法第四十六條第一項第八款至第十款規定工作之外國人請假返國辦法',
 '家庭暴力被害人就業服務辦法',
 '被裁減資遣被保險人繼續參加勞工保險及保險給付辦法',
 '移動式起重機安全檢查構造標準',
 '私立就業服務機構許可及管理辦法',
 '新化學物質登記管理辦法',
 '最低工資法（112.12.27制定）',
 '身心障礙者定額進用不列入員工總人數計算單位職務分析標準',
 '雇主聘僱本國籍照顧服務員補助辦法',
 '外國專業人才從事藝術工作許可及管理辦法',
 '工會財務處理準則',
 '勞工職業災害保險被保險人退保後診斷罹患職業病補助及津貼核發辦法',
 '勞工保險局作業基金收支保管及運用辦法',
 '勞資爭議法律及生活費用扶助辦法',
 '職業安全衛生教育訓練規則',
 '勞工職業災害保險預防職業病健康檢查及健康追蹤檢查辦法',
 '安全標示與驗證合格標章使用及管理辦法',
 '勞動檢查法施行細則',
 '因應貿易自由化勞工就業調整支援措施實施辦法',
 '起重升降機具安全規則',
 '直轄市勞動檢查機構組織準則',
 '勞工作業場所容許暴露標準',
 '辦理勞工體格與健康檢查醫療機構認可及管理辦法',
 '視覺功能障礙者按摩工作輔導及補助辦法',
 '就業保險延長失業給付實施辦法',
 '勞動基準法檢舉案件保密及處理辦法',
 '管制性化學品之指定及運作許可管理辦法',
 '性別平等工作法',
 '勞工保險條例',
 '性別平等工作法施行細則',
 '災區受災勞工保險與勞工職業災害保險及就業保險被保險人保險費支應及傷病給付辦法',
 '職業災害勞工醫療期間退保繼續參加勞工保險辦法',
 '技能職類測驗能力認證及管理辦法',
 '四烷基鉛中毒預防規則',
 '大量解僱勞工訴訟及必要生活費用補助辦法',
 '職業訓練基金設置管理運用辦法',
 '固定式起重機安全檢查構造標準',
 '大量解僱勞工保護法',
 '公立就業服務機構設置準則',
 '勞工職業災害保險及保護法第十條規定參加保險辦法',
 '職業安全衛生法施行細則',
 '進用身心障礙者工作績優機關（構）獎勵辦法',
 '勞工保險被保險人轉投軍人保險公教人員保險年資保留辦法',
 '技能職類證書發證及管理辦法',
 '勞工保險未繳還之保險給付及貸款本息扣減辦法',
 '勞工退休金條例退休基金管理運用及盈虧分配辦法',
 '不當勞動行為裁決辦法',
 '身心障礙者就業基金撥交就業安定基金提撥及分配辦法',
 '人口販運被害人工作許可及管理辦法',
 '危險性工作場所審查及檢查辦法',
 '危險性機械或設備代行檢查機構管理規則',
 '在職中高齡者及高齡者穩定就業辦法',
 '人力供應業個人資料檔案安全維護計畫及處理辦法',
 '工業用機器人危害預防標準',
 '勞動基準法',
 '職業醫學科專科醫師及地區醫院以上之醫院專科醫師開具職業病門診單辦法',
 '雇主聘僱外國人許可及管理辦法',
 '私立就業服務機構收費項目及金額標準',
 '勞工退休基金收支保管及運用辦法',
 '異常氣壓危害預防標準',
 '職業災害勞工申請器具照護失能及死亡補助辦法',
 '就業促進津貼實施辦法',
 '壓力容器安全檢查構造標準',
 '職業安全衛生管理辦法',
 '中高齡者及高齡者就業促進法',
 '勞工職業災害保險醫療給付項目及支付標準',
 '勞工保險條例施行細則',
 '就業保險之職業訓練及訓練經費管理運用辦法',
 '勞動檢查法第二十八條所定勞工有立即發生危險之虞認定標準',
 '哺集乳室與托兒設施措施設置標準及經費補助辦法',
 '職工福利金條例',
 '勞工職業災害保險職業病鑑定作業實施辦法',
 '勞工健康保護規則',
 '勞工退休金條例',
 '身心障礙者職業輔導評量實施方式及補助準則',
 '勞資爭議處理法',
 '勞工保險爭議事項審議辦法',
 '勞資會議實施辦法',
 '勞工職業災害保險及保護法施行細則',
 '妊娠與分娩後女性及未滿十八歲勞工禁止從事危險性或有害性工作認定標準',
 '技能競賽實施及獎勵辦法',
 '身心障礙者職業訓練機構設立管理及補助準則',
 '育嬰留職停薪實施辦法',
 '製程安全評估定期實施辦法',
 '推動國民就業績優評選及獎勵辦法',
 '職業災害預防補助辦法',
 '民間參與勞工福利設施接管營運辦法',
 '碼頭裝卸安全衛生設施標準',
 '粉塵危害預防標準',
 '地方政府成立銀髮人才服務據點補助辦法',
 '就業服務法施行細則',
 '就業保險法施行細則',
 '勞工請假規則',
 '構造規格特殊產品安全評估報告及檢驗辦法',
 '職業災害勞工職業重建補助辦法',
 '勞動部受理外國專業人才延攬及僱用法申請案件收費標準',
 '職業災害勞工保護法',
 '勞動部積欠工資墊償基金管理委員會組織規程',
 '政府機關推動職業安全衛生業務績效評核及獎勵辦法',
 '機械類產品申請先行放行辦法',
 '取得華僑身分香港澳門居民聘僱及管理辦法',
 '職業災害勞工保護法施行細則',
 '勞資爭議調解辦法',
 '身心障礙者職務再設計實施方式及補助準則',
 '職業災害勞工職能復健專業機構認可管理及補助辦法',
 '就業服務法申請案件審查費及證照費收費標準',
 '退休中高齡者及高齡者再就業補助辦法',
 '促進職業安全衛生文化獎勵及補助辦法',
 '精密作業勞工視機能保護設施標準',
 '技術士技能檢定及發證辦法',
 '勞工退休準備金提撥及管理辦法',
 '職業安全衛生顧問服務機構審查收費標準',
 '勞工保險基金管理及運用辦法',
 '性別平等工作法律扶助辦法',
 '職業災害預防及職業災害勞工重建補助辦法（111.03.31訂定）',
 '直轄市及縣市政府辦理協助職業災害勞工重返職場補助辦法',
 '職業訓練師甄審遴聘辦法',
 '高壓氣體勞工安全規則',
 '職業訓練機構設立及管理辦法',
 '機械設備器具安全標準',
 '既有危險性機械及設備安全檢查規則',
 '職業養成訓練及轉業訓練委任或委託辦法',
 '積欠工資墊償基金提繳及墊償管理辦法',
 '家庭暴力被害人創業貸款補助辦法',
 '吊籠安全檢查構造標準',
 '勞工保險被保險人退保後罹患職業病者請領職業災害保險失能給付辦法',
 '技術士技能檢定作業及試場規則',
 '職工福利金條例施行細則',
 '職工福利委員會組織準則',
 '職業安全衛生標示設置準則',
 '勞工作業環境監測實施辦法',
 '財團法人職業災害預防及重建中心監督及管理辦法',
 '高溫作業勞工作息時間標準',
 '勞工職業災害保險年金給付併領調整辦法',
 '危險性機械及設備安全檢查規則',
 '鍋爐及壓力容器安全規則',
 '身心障礙者庇護工場設立管理及補助準則',
 '危害性化學品標示及通識規則',
 '大量解僱勞工時勞動市場變動趨勢評估委員會組織辦法',
 '勞工職業災害保險失能給付標準',
 '勞工職業災害保險未繳還之保險給付扣減辦法',
 '機械類產品申請免驗證辦法',
 '事業單位僱用女性勞工夜間工作場所必要之安全衛生設施標準',
 '職業傷病診治醫療機構認可管理補助及職業傷病通報辦法',
 '職業安全衛生設施規則',
 '勞動檢查員執行職務迴避辦法',
 '勞動檢查法',
 '技術士技能檢定規費收費標準',
 '人力仲介業個人資料檔案安全維護計畫及處理辦法',
 '公立就業服務機構就業諮詢及職業輔導實施辦法',
 '管制性化學品許可申請收費標準',
 '工會法施行細則',
 '就業安定基金收支保管及運用辦法',
 '勞工職業災害保險實績費率計算及調整辦法',
 '外國人受聘僱從事就業服務法第四十六條第一項第八款至第十一款規定工作之轉換雇主或工作程序準則',
 '工作場所性騷擾防治措施準則',
 '勞工退休準備金資料提供金融機構處理辦法',
 '就業保險失業者創業協助辦法',
 '勞工退休金條例施行細則',
 '工會會員大會或會員代表大會委託出席辦法',
 '原住民待工期間職前訓練經費補助辦法',
 '青年跨域就業促進補助實施辦法',
 '外國人從事就業服務法第四十六條第一項第一款至第六款工作資格及審查標準',
 '職業安全衛生法',
 '辦理勞工體格與健康檢查醫療機構認可審查收費標準',
 '勞動基準法第四十五條無礙身心健康認定基準及審查辦法',
 '大量解僱勞工時禁止事業單位代表人及實際負責人出國處理辦法',
 '身心障礙者職業重建服務專業人員遴用及培訓準則',
 '就業服務法',
 '勞工職業災害保險職業傷病審查準則',
 '團體協約法',
 '勞資爭議仲裁辦法',
 '性別平等工作申訴審議處理辦法',
 '庇護工場身心障礙者職業災害補償費用補助辦法',
 '就業保險促進就業實施辦法',
 '中高齡者及高齡者就業促進法施行細則',
 '促進中高齡者及高齡者就業獎勵辦法',
 '雇主聘僱外國人從事家庭看護工作或家庭幫傭聘前講習實施辦法',
 '勞動檢查員遴用及專業訓練辦法',
 '私立職業訓練機構個人資料檔案安全維護計畫及處理辦法',
 '特殊境遇家庭創業貸款補助辦法',
 '重體力勞動作業勞工保護措施標準',
 '礦場職業衛生設施標準',
 '缺氧症預防規則',
 '失業中高齡者及高齡者就業促進辦法',
 '勞動部對受嚴重特殊傳染性肺炎影響勞工紓困辦法',
 '勞動部主管職工福利委員會財團法人工作計畫經費預算工作報告及財務報表編製辦法',
 '特定化學物質危害預防標準',
 '身心障礙者就業服務機構設立管理及補助準則',
 '高架作業勞工保護措施標準',
 '危險性機械及設備檢查費收費標準',
 '勞動契約法',
 '工會法',
 '勞動基準法施行細則',
 '國際組織技能競賽國家代表隊服補充兵役辦法',
 '身心障礙者創業輔導服務實施方式及補助準則',
 '職業訓練法施行細則',
 '職業訓練師與學校教師年資相互採計及待遇比照辦法',
 '勞工教育實施辦法',
 '短期補習班聘僱外國專業人才從事教師工作資格及審查標準',
 '職業訓練法',
 '勞工退休金條例年金保險實施辦法',
 '就業保險法',
 '女性勞工母性健康保護實施辦法',
 '機械設備器具監督管理辦法',
 '勞工職業災害保險及保護法',
 '機械類產品型式驗證實施及監督管理辦法',
 '職業訓練師培訓辦法',
 '外國人從事就業服務法第四十六條第一項第八款至第十一款工作資格及審查標準',
 '職業災害勞工補助及核發辦法',
 '失業被保險人及其眷屬全民健康保險保險費補助辦法',
 '危害性化學品評估及分級管理辦法',
 '職業安全衛生顧問服務機構與其顧問服務人員之認可及管理規則',
 '技能職類測驗能力認證審查費收費辦法',
 '事業單位勞工退休準備金監督委員會組織準則',
 '有機溶劑中毒預防規則',
 '機械設備器具安全資訊申報登錄辦法',
 '勞動部主管職工福利委員會財團法人會計處理及財務報告編製準則',
 '勞工保險預防職業病健康檢查辦法（85.06.29訂定）']
 