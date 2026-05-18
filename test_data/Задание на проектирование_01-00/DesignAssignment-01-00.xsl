<?xml version="1.0" encoding="UTF-8"?>

<!--
ID версии визуализации указывается в формате SS.SS.TT, где 
	SS.SS - номер версии XML-схемы, 
	TT    - номер версии визуализациии к XML-схеме
-->

<xsl:stylesheet id="01.00.01" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="html" media-type = "text/html" encoding="UTF-8" omit-xml-declaration="yes" doctype-public="/"/> 
	
	<xsl:template match="/">
		<xsl:choose>
			<xsl:when test="/Document/@SchemaVersion != '01.00'">
				<p>НОМЕР ВЕРСИИ XML-СХЕМЫ ДОКУМЕНТА НЕ СООТВЕТСТВУЕТ ТРЕБУЕМОМУ '01.00'</p>
			</xsl:when>
			<xsl:when test="/Document/@TypeCode != '05.03'">
				<p>КОД ВИДА ДОКУМЕНТА НЕ СООТВЕТСТВУЕТ ТРЕБУЕМОМУ '05.03'</p>
			</xsl:when>
			<xsl:otherwise>
				<xsl:apply-templates select="Document"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
		
	<xsl:key name="DocumentsInfoById" match="//DocumentInfo" use="@Id" />
	
	<xsl:template match="Document">
		<html>
			<head>
				<title><xsl:value-of select="Requisites/Number"/></title>
				<style type='text/css'>
					body {
						font-family: Times New Roman;
						font-size: 15px;
						width: 800px;
						margin: 2em auto;
						text-align:left;
					}
					table {
						border-collapse:collapse;
						margin:0.5em 0;
						width:100%;
					}
					td,th {
						border: 1px solid black;
						padding: 0.2em 0.4em;
					}
					thead tr, tfoot tr{
						font-weight: bold;
						text-align: center;
						color:#444;
					}
					
					thead tr.border-bottom {
						border-bottom: 2px solid #666;
					}
					td a {
						display: block;
					}
					td.title {
						border: 1px dashed black;
						text-align:center;
						padding:1em;
					}
					.not-border {
						border:0;
					}
					p {
						padding: 0.2em 0;
						margin:auto;
						color:black;
					}
					p.border {
						border:1px solid #444;
						padding: 0.4em;
						margin: 0.4em 0;
					}
					p.black {
						border-color:black;
					}
					p.under-text-line {
						border-top:1px solid #bbb;
						color:#555;
						padding:0;
						margin:0;
					}
					p.red-string {
						text-indent: 0em;
					}
					p.margin-vertical {
						marfin: 2px 0;
					}
					p.pad-left{
						padding-left:0.5em;
					}
					b{
						color:#444;
					}
					h1 {
						font-size:18px;
						font-weight:bold;
						text-align:center;
						padding:0.5em;
						margin-top:2em;
					}
					h2 {
						font-size:17px;
						font-weight:bold;
						text-align:left;
						padding:0.5em;
						margin-top:2em;
					}
					h3 {
						font-size: 16px;
						font-weight: bold;
						text-align: left;
						padding:0.5em;
						margin-top:1em;
					}
					h4 {
						font-size: 15px;
						font-weight: bold;
						text-align: left;
						padding-left: 0.5em;
					}
					h5 {
						font-size: 15px;
						font-weight: bold;
						margin: 1em 0em;
						text-align: center;
						color:#333;
					}
					.bckgr{
						background-color:#ddd;
					}
					.bckgr-list{
						background-color:#ebebeb;
					}
					.upper{
						text-transform:uppercase;
					}
					.margin-top-small{
						margin-top:1em;
					}
					.margin-bottom-small{
						margin-bottom:2em;
					}
					a {
						color:black;
						text-decoration: none;
					}
					.clear {
						margin-bottom:0;
						margin-top:3em;
						padding:0;
					}
					.left {
						text-align: left;
					}
					.right {
						text-align: right;
					}					
					.justify {
						text-align: justify;
					}
					.center {
						text-align: center;
					}
					.bold {
						font-weight: bold;
					}
					.under {
						text-decoration:underline;
					}
					.italic {
						font-style: italic;
					}
					img {
						max-width:100%;
						margin:0.5em 0;
					}
					i {
						padding-right:5px;
						font-style:normal;
					}
					@media (min-width: 1200px){
							div.leftMenu {
							position:fixed;
							top:1.5em;
							left:0;
							cursor:pointer;
						}
					}
					@media (max-width: 1200px){
						div.leftMenu {
						display:none;
						}
					}
					nav ul {
						padding: 0;
						margin: 0;
						list-style: none;
						position: relative;
						font-size: 15px;
						text-decoration: none;
					}
					nav ul li {
						display: block;
						background-color: white;
					}
					nav a {
						display: block;
						padding: 2px 5px 2px 5px;
						border: 1px solid white;
						font-size: 15px;
						font-weight: normal;
						text-decoration: none;
					}
					nav a:hover {
						background-color: #bedcf7;
						text-decoration: none;
					}
					nav ul ul {
						display: none;
						position: absolute;
						top: 0;
						left:175px;
					}
					nav ul li:hover > ul {
						display: inherit;
					}
					nav ul ul li {
						min-width: 300px;
						border: 0;
						border-left: 3px solid #aaa;
						float: none;
						display: list-item;
						position: relative;
						z-index: 20;
						background-color: #efefef;
					}
				</style>
			</head>
			<body>
				<xsl:call-template name="TitleSection"/>
				
				<xsl:call-template name="ChaptersSection"/>
				
				<a name="chI"/>
				<h2 class="center bckgr upper">I. Общие данные</h2>

				<xsl:call-template name="Objective"/>
				
				<xsl:call-template name="DecisionDocuments"/>
				
				<xsl:call-template name="Developers"/>
				
				<xsl:call-template name="TechnicalCustomer"/>
				
				<xsl:apply-templates select="/Document/Content/Designers"/>
				
				<xsl:call-template name="ConstructionTypeDates"/>				
				
				<xsl:call-template name="Stages"/>
				
				<xsl:apply-templates select="/Document/Content/FinanceSources"/>
				
				<xsl:call-template name="Specifications"/>
				
				<xsl:call-template name="ObjectTEI"/>
				
				<xsl:call-template name="ObjectMainInfo"/>
				
				<xsl:apply-templates select="/Document/Content/DesignPhases"/>
				
				<xsl:call-template name="JustificationSafety"/>

				<xsl:call-template name="QualitySolutions"/>

				<xsl:apply-templates select="/Document/Content/EngineeringSurvey"/>

				<xsl:call-template name="MarginalCost"/>

				<xsl:call-template name="CommissioningConditions"/>
				
				<xsl:call-template name="AdjacentsObjects"/>				
								
				<xsl:call-template name="SpecialConditions"/>

				<a name="chII"/>
				<h2 class="center bckgr upper">II. Перечень основных требований к проектным решениям</h2>

				<xsl:call-template name="ObjectsProjectSolutions"/>

				<a name="chIII"/>
				<h2 class="center bckgr upper">III. Иные требования к проектированию</h2>
				
				<xsl:call-template name="ObjectsProjectDocuments"/>
				
				<xsl:call-template name="ObjectOtherRequirements"/>
				
				<xsl:call-template name="Agreements"/>
				
				<xsl:apply-templates select="/Document/Content/InitialDocuments"/>

				<xsl:call-template name="AgreementsSection"/>
				
				<xsl:call-template name="LeftMenu"/>
			</body>
		</html>
	</xsl:template>
	<!-- Конец основного шаблона -->
	
	<xsl:template name="TitleSection">
		<table>
			<tr valign="top">
				<td class="not-border" width="70%">
					<p><b>УТВЕРЖДЕНО:</b></p><br/>
					<xsl:for-each select="/Document/Requisites/Authors/Author//*[@FunctionalRole=1]">
						<xsl:if test="name()='Representative'">
							
							<p class="upper">юридическеое лицо</p>
							<p><xsl:value-of select="../../Organization/FullName"/></p>
							<p><xsl:value-of select="Position"/></p>
							<p><b>
								<i><xsl:value-of select="Surname"/></i><xsl:text> </xsl:text> 
								<i><xsl:value-of select="Name"/></i><xsl:text> </xsl:text>
								<xsl:value-of select="Patronymic"/>
							</b></p>
							<br/>
						</xsl:if>
						
						<xsl:if test="name()='IndividualEntrepreneur'">
							
							<p class="upper">индивидуальный предприниматель</p>
							<p class="upper">ОГРНИП: <xsl:value-of select="OGRNIP"/></p>
							<p><b>
								<i><xsl:value-of select="Surname"/></i><xsl:text> </xsl:text>
								<i><xsl:value-of select="Name"/></i><xsl:text> </xsl:text>
								<xsl:value-of select="Patronymic"/>
							</b></p>
							<br/>
						</xsl:if>
						<xsl:if test="name()='Person'">
							
							<p class="upper">физическое лицо</p>
							<!--
							<p class="upper">СНИЛС: <xsl:value-of select="SNILS"/></p>
							-->
							<p><b>
								<i><xsl:value-of select="Surname"/></i><xsl:text> </xsl:text>
								<i><xsl:value-of select="Name"/></i><xsl:text> </xsl:text>
								<xsl:value-of select="Patronymic"/>
							</b></p>
							<br/>							
						</xsl:if>
					</xsl:for-each>
				</td>
				<td class="left not-border">
					<p class="upper"><xsl:apply-templates select="/Document/Requisites/SecurityLabel"/></p>
				</td>
			</tr>
			<tr><td class="not-border">
				<p></p>
			</td></tr>			
			<tr>
				<td class="title" colspan="2">
					<h1 class="upper">Задание на проектирование<br/>объекта капитального строительства</h1>
					
					<xsl:if test="/Document/Requisites/Number != ''">
						<h2 class="center">№ <xsl:value-of select="/Document/Requisites/Number"/></h2>	
					</xsl:if>					
					
					<h2 class="center upper clear"><xsl:value-of select="/Document/Content/Object/Name"/></h2>
					
					<p class="under-text-line">наименование объекта капитального строительства (далее - объект)</p>
					
					<xsl:if test="/Document/Content/Object/Address">
						<h2 class="center clear">
							<xsl:apply-templates select="/Document/Content/Object/Address"/>
						</h2>
						<p class="under-text-line">адрес (местоположение) объекта</p>
					</xsl:if>
					<xsl:if test="/Document/Content/Object/BeginAddress">
						<h2 class="center clear">
							<xsl:apply-templates select="/Document/Content/Object/BeginAddress"/>
						</h2>
						<p class="under-text-line">Адрес (местоположение) начального пункта линейного объекта</p>
						<h2 class="center clear">
							<xsl:apply-templates select="/Document/Content/Object/FinalAddress"/>
						</h2>
						<p class="under-text-line">Адрес (местоположение) конечного пункта линейного объекта</p>
					</xsl:if>
					
					<br/><br/>
					<table>
						<thead>
							<tr><td colspan="2" width="60%">Предыдущие версии документа</td><td rowspan="2" width="40%">Порядковый номер текущей версии документа</td></tr>
							<tr><td width="30%">Порядковый номер версии</td><td width="30%">Контрольная сумма файла версии документа</td></tr>	
						</thead>
						<tbody>
							<xsl:for-each select="/Document/Versions/Version">
								<xsl:sort select="@VersionNumber"/>
								<tr>
									<td><xsl:value-of select="@VersionNumber"/></td>
									<td><xsl:value-of select="@Checksum"/></td>
									<xsl:if test="position() = 1">
										<td>
											<xsl:attribute name="rowspan">
												<xsl:value-of select="count(/Document/Versions/Version)"/>
											</xsl:attribute>
											<b><xsl:value-of select="/Document/@VersionNumber"/></b>
										</td>
									</xsl:if>
								</tr>
							</xsl:for-each>
							<xsl:if test="not(/Document/Versions)">
								<tr>
									<td colspan="2">отсутствуют</td>
									<td><b><xsl:value-of select="/Document/@VersionNumber"/></b></td>
								</tr>
							</xsl:if>
						</tbody>
					</table>
				</td>
			</tr>
		</table>
		<p class="center">
			<xsl:value-of select="substring(/Document/Requisites/Date,1,4)"/>
		</p>
	</xsl:template>
	
	<xsl:template name="ChaptersSection">
		<a name="Chapters"/>
		<h2 class="bckgr upper center">Состав задания на проектирование</h2>
		
		<table id="chapterstable">
			<tr class="bold center"><td width="5%">№ <nobr>п/п</nobr></td><td>Наименование раздела</td></tr>
			<tr class="bold"><td colspan="2"><a href="#chI">I. Общие данные</a></td></tr>
			<tr><td>1.</td><td><a href="#ch1">Цель реализации проекта</a></td></tr>
			<tr><td>2.</td><td><a href="#ch2">Основание для проектирования объекта</a></td></tr>
			<tr><td>3.</td><td><a href="#ch3">Застройщик</a></td></tr>
			<tr><td>4.</td><td><a href="#ch4">Технический заказчик</a></td></tr>
			<tr><td>5.</td><td><a href="#ch5">Разработчик проектной документации</a></td></tr>
			<tr><td>6.</td><td><a href="#ch6">Вид и срок строительства объекта</a></td></tr>
			<tr><td>7.</td><td><a href="#ch7">Требования к выделению этапов строительства объекта</a></td></tr>
			<tr><td>8.</td><td><a href="#ch8">Источник финансирования строительства объекта</a></td></tr>
			<tr><td>9.</td><td><a href="#ch9">Технические условия на подключение (присоединение) объекта к сетям инженерно-технического обеспечения</a></td></tr>
			<tr><td>10.</td><td><a href="#ch10">Требования к основным технико-экономическим показателям</a></td></tr>
			<tr><td>11.</td><td><a href="#ch11">Общие сведения и идентификационные признаки</a></td></tr>
			<tr><td>12.</td><td><a href="#ch12">Стадийность проектирования и задачи</a></td></tr>
			<tr><td>13.</td><td><a href="#ch13">Требования о необходимости соответствия проектной документации обоснованию безопасности опасного производственного объекта</a></td></tr>
			<tr><td>14.</td><td><a href="#ch14">Требования к качеству, конкурентоспособности, экологичности и энергоэффективности проектных решений</a></td></tr>
			<tr><td>15.</td><td><a href="#ch15">Необходимость выполнения инженерных изысканий для подготовки проектной документации</a></td></tr>
			<tr><td>16.</td><td><a href="#ch16">Предполагаемая (предельная) стоимость строительства объекта</a></td></tr>
			<tr><td>17.</td><td><a href="#ch17">Условия ввода в эксплуатацию</a></td></tr>
			<tr><td>18.</td><td><a href="#ch18">Смежные объекты капитального строительства</a></td></tr>
			<tr><td>19.</td><td><a href="#ch19">Особые условия строительства</a></td></tr>
			
			<tr class="bold"><td colspan="2"><a href="#chII">II. Перечень основных требований к проектным решениям</a></td></tr>
			<tr><td>20.</td><td><a href="#ch20">Требования к схеме планировочной организации земельного участка</a></td></tr>
			<tr><td>21.</td><td><a href="#ch21">Требования к проекту полосы отвода</a></td></tr>
			<tr><td>22.</td><td><a href="#ch22">Требования к архитектурно-художественным решениям, включая требования к графическим материалам</a></td></tr>
			<tr><td>23.</td><td><a href="#ch23">Требования к технологическим решениям</a></td></tr>
			<tr><td>24.</td><td><a href="#ch24">Требования к конструктивным и объемно-планировочным решениям</a></td></tr>
			<tr><td>25.</td><td><a href="#ch25">Требования к технологическим и конструктивным решениям линейного объекта</a></td></tr>
			<tr><td>26.</td><td><a href="#ch26">Требования к зданиям, строениям и сооружениям, входящим в инфраструктуру линейного объекта</a></td></tr>
			<tr><td>27.</td><td><a href="#ch27">Требования к инженерно-техническим решениям</a></td></tr>
			<tr><td>28.</td><td><a href="#ch28">Требования к мероприятиям по охране окружающей среды</a></td></tr>
			<tr><td>29.</td><td><a href="#ch29">Требования к мероприятиям по обеспечению пожарной безопасности</a></td></tr>
			<tr><td>30.</td><td><a href="#ch30">Требования к мероприятиям по обеспечению соблюдения требований энергетической эффективности и по оснащенности объекта приборами учета используемых энергетических ресурсов</a></td></tr>
			<tr><td>31.</td><td><a href="#ch31">Требования к мероприятиям по обеспечению доступа маломобильных групп населения к объекту</a></td></tr>
			<tr><td>32.</td><td><a href="#ch32">Требования к инженерно-техническому укреплению объекта в целях обеспечения его антитеррористической защищенности</a></td></tr>
			<tr><td>33.</td><td><a href="#ch33">Требования к соблюдению безопасных для здоровья человека условий проживания и пребывания в объекте и требования к соблюдению безопасного уровня воздействия объекта на окружающую среду</a></td></tr>
			<tr><td>34.</td><td><a href="#ch34">Требования к технической эксплуатации и техническому обслуживанию объекта</a></td></tr>
			<tr><td>35.</td><td><a href="#ch35">Требования к проекту организации строительства объекта</a></td></tr>
			<tr><td>36.</td><td><a href="#ch36">Требования о необходимости сноса или сохранения зданий, сооружений, вырубки или сохранения зеленых насаждений, реконструкции, капитального ремонта существующих линейных объектов в связи с планируемым строительством объекта, расположенных на земельном участке, на котором планируется строительство объекта</a></td></tr>
			<tr><td>37.</td><td><a href="#ch37">Требования к решениям по благоустройству прилегающей территории, малым архитектурным формам и планировочной организации земельного участка</a></td></tr>
			<tr><td>38.</td><td><a href="#ch38">Требования к разработке проекта рекультивации земель</a></td></tr>
			<tr><td>39.</td><td><a href="#ch39">Требования к местам складирования излишков грунта и (или) мусора при строительстве и протяженность маршрута их доставки</a></td></tr>
			<tr><td>40.</td><td><a href="#ch40">Требования к выполнению научно-исследовательских и опытно-конструкторских работ в процессе проектирования и строительства объекта</a></td></tr>
			
			<tr class="bold"><td colspan="2"><a href="#chIII">III. Иные требования к проектированию</a></td></tr>
			<tr><td>41.</td><td><a href="#ch41">Требования к составу проектной документации, в том числе требования о разработке разделов проектной документации, наличие которых не является обязательным</a></td></tr>
			<tr><td>42.</td><td><a href="#ch42">Требования к подготовке сметной документации</a></td></tr>
			<tr><td>43.</td><td><a href="#ch43">Требования к разработке специальных технических условий</a></td></tr>
			<tr><td>44.</td><td><a href="#ch44">Требования о применении при разработке проектной документации документов в области стандартизации</a></td></tr>
			<tr><td>45.</td><td><a href="#ch45">Требования к выполнению демонстрационных материалов, макетов</a></td></tr>
			<tr><td>46.</td><td><a href="#ch46">Требования о подготовке проектной документации, содержащей материалы в форме информационной модели</a></td></tr>
			<tr><td>47.</td><td><a href="#ch47">Требование о применении типовой проектной документации, типового проектного решения</a></td></tr>
			<tr><td>48.</td><td><a href="#ch48">Прочие дополнительные требования и указания, конкретизирующие объём проектных работ</a></td></tr>
			<tr><td>49.</td><td><a href="#ch49">Перечень необходимых согласований</a></td></tr>
			<tr><td>50.</td><td><a href="#ch50">Материалы, предоставляемые застройщиком (техническим заказчиком)</a></td></tr>
			
			
			<tr class="bold"><td colspan="2"><a href="#chIV">IV. Лист согласования задания на проектирование</a></td></tr>
		</table>
	</xsl:template>

	<xsl:template name="LeftMenu">
		<div class="leftMenu">
			<nav>
				<ul><a href="#Chapters" title="Состав задания на проектирование">СОСТАВ ЗАДАНИЯ</a></ul>
				<ul>
					<li>
						<a href="#chI" title="I. Общие данные">ОБЩИЕ ДАННЫЕ</a>
						<ul>
							<li><a href="#ch1" title="Цель реализации проекта">1.Цель реализации</a></li>
							<li><a href="#ch2" title="Основание для проектирования объекта">2. Основание для проектирования</a></li>
							<li><a href="#ch3" title="Застройщик">3. Застройщик</a></li>
							<li><a href="#ch4" title="Технический заказчик">4. Технический заказчик</a></li>
							<li><a href="#ch5" title="Разработчик проектной документации">5. Проектировщик</a></li>
							<li><a href="#ch6" title="Вид и срок строительства объекта">6. Вид и срок строительства</a></li>
							<li><a href="#ch7" title="Требования к выделению этапов строительства объекта">7. Выделение этапов</a></li>
							<li><a href="#ch8" title="Источник финансирования строительства объекта">8. Финансирование</a></li>
							<li><a href="#ch9" title="Технические условия на подключение (присоединение) объекта к сетям инженерно-технического обеспечения">9. Технические условия</a></li>
							<li><a href="#ch10" title="Требования к основным технико-экономическим показателям">10. Технико-экономические показатели</a></li>
							<li><a href="#ch11" title="Общие сведения и идентификационные признаки">11. Идентификационные признаки</a></li>
							<li><a href="#ch12" title="Стадийность проектирования и задачи">12. Стадийность проектирования</a></li>
							<li><a href="#ch13" title="Требования о необходимости соответствия проектной документации обоснованию безопасности опасного производственного объекта">13. Соответствие обоснованию безопасности</a></li>
							<li><a href="#ch14" title="Требования к качеству, конкурентоспособности, экологичности и энергоэффективности проектных решений">14. Качество, конкурентоспособность</a></li>
							<li><a href="#ch15" title="Необходимость выполнения инженерных изысканий для подготовки проектной документации">15. Инженерные изыскания</a></li>
							<li><a href="#ch16" title="Предполагаемая (предельная) стоимость строительства объекта">16. Стоимость строительства</a></li>
							<li><a href="#ch17" title="Условия ввода в эксплуатацию">17. Условия ввода в эксплуатацию</a></li>
							<li><a href="#ch18" title="Смежные объекты капитального строительства">18. Смежные объекты</a></li>
							<li><a href="#ch19" title="Особые условия строительства">19. Особые условия</a></li>
						</ul>
					</li>
				</ul>
				<ul>
					<li>
						<a href="#chII" title="II. Перечень основных требований к проектным решениям">ПРОЕКТНЫЕ РЕШЕНИЯ</a>
						<ul>
							<li><a href="#ch20" title="Требования к схеме планировочной организации земельного участка">20. Схема планировочной организации</a></li>
							<li><a href="#ch21" title="Требования к проекту полосы отвода">21. Проект полосы отвода</a></li>
							<li><a href="#ch22" title="Требования к архитектурно-художественным решениям, включая требования к графическим материалам">22. Архитектурно-художественные решения</a></li>
							<li><a href="#ch23" title="Требования к технологическим решениям">23. Технологические решения</a></li>
							<li><a href="#ch24" title="Требования к конструктивным и объемно-планировочным решениям">24. Конструктивные и объемно-планировочные решения</a></li>
							<li><a href="#ch25" title="Требования к технологическим и конструктивным решениям линейного объекта">25. Технологические и конструктивные решения линейного объекта</a></li>
							<li><a href="#ch26" title="Требования к зданиям, строениям и сооружениям, входящим в инфраструктуру линейного объекта">26. Здания, строения линейного объекта</a></li>
							<li><a href="#ch27" title="Требования к инженерно-техническим решениям">27. Инженерно-технические решения</a></li>
							<li><a href="#ch28" title="Требования к мероприятиям по охране окружающей среды">28. Охрана окружающей среды</a></li>
							<li><a href="#ch29" title="Требования к мероприятиям по обеспечению пожарной безопасности">29. Пожарная безопасность</a></li>
							<li><a href="#ch30" title="Требования к мероприятиям по обеспечению соблюдения требований энергетической эффективности и по оснащенности объекта приборами учета используемых энергетических ресурсов">30. Энергетическая эффективность</a></li>
							<li><a href="#ch31" title="Требования к мероприятиям по обеспечению доступа маломобильных групп населения к объекту">31. Маломобильные группы населения</a></li>
							<li><a href="#ch32" title="Требования к инженерно-техническому укреплению объекта в целях обеспечения его антитеррористической защищенности">32. Инженерно-техническое укрепление</a></li>
							<li><a href="#ch33" title="Требования к соблюдению безопасных для здоровья человека условий проживания и пребывания в объекте и требования к соблюдению безопасного уровня воздействия объекта на окружающую среду">33. Условия проживания и пребывания</a></li>
							<li><a href="#ch34" title="Требования к технической эксплуатации и техническому обслуживанию объекта">34. Эксплуатация</a></li>
							<li><a href="#ch35" title="Требования к проекту организации строительства объекта">35. Организация строительства</a></li>
							<li><a href="#ch36" title="Требования о необходимости сноса или сохранения зданий, сооружений, вырубки или сохранения зеленых насаждений, реконструкции, капитального ремонта существующих линейных объектов в связи с планируемым строительством объекта, расположенных на земельном участке, на котором планируется строительство объекта">36. Необходимость сноса, сохранения</a></li>
							<li><a href="#ch37" title="Требования к решениям по благоустройству прилегающей территории, малым архитектурным формам и планировочной организации земельного участка">37. Благоустройство</a></li>
							<li><a href="#ch38" title="Требования к разработке проекта рекультивации земель">38. Рекультивация</a></li>
							<li><a href="#ch39" title="Требования к местам складирования излишков грунта и (или) мусора при строительстве и протяженность маршрута их доставки">39. Места складирования</a></li>
							<li><a href="#ch40" title="Требования к выполнению научно-исследовательских и опытно-конструкторских работ в процессе проектирования и строительства объекта">40. Научно-исследовательские работы</a></li>
						</ul>
					</li>
				</ul>
				<ul>
					<li>
						<a href="#chIII" title="III. Иные требования к проектированию">ИНЫЕ ТРЕБОВАНИЯ</a>
						<ul>
							<li><a href="#ch41" title="Требования к составу проектной документации, в том числе требования о разработке разделов проектной документации, наличие которых не является обязательным">41. Состав проектной документации</a></li>
							<li><a href="#ch42" title="Требования к подготовке сметной документации">42. Сметная документация</a></li>
							<li><a href="#ch43" title="Требования к разработке специальных технических условий">43. Специальные технические условия</a></li>
							<li><a href="#ch44" title="Требования о применении при разработке проектной документации документов в области стандартизации">44. Документы в области стандартизации</a></li>
							<li><a href="#ch45" title="Требования к выполнению демонстрационных материалов, макетов">45. Демонстрационные материалы</a></li>
							<li><a href="#ch46" title="Требования о подготовке проектной документации, содержащей материалы в форме информационной модели">46. Информационная модель</a></li>
							<li><a href="#ch47" title="Требование о применении типовой проектной документации, типового проектного решения">47. Типовая документация и решения</a></li>
							<li><a href="#ch48" title="Прочие дополнительные требования и указания, конкретизирующие объём проектных работ">48. Прочие дополнительные требования</a></li>
							<li><a href="#ch49" title="Перечень необходимых согласований">49. Перечень согласований</a></li>
							<li><a href="#ch50" title="Материалы, предоставляемые застройщиком (техническим заказчиком)">50. Предоставляемые материалы</a></li>
						</ul>
					</li>
				</ul>
				<ul><a href="#chIV" title="IV. Лист согласования задания на проектирование">ЛИСТ СОГЛАСОВАНИЯ</a></ul>
			</nav>
		</div>
	</xsl:template>

	<xsl:template name="AgreementsSection">
		<a name="chIV"/>
		<h2 class="bckgr upper center">IV. Лист согласования задания на проектирование</h2>
		
		<xsl:for-each select="/Document/Requisites/Authors/Author">

			<xsl:if test="Organization and count(Representatives/Representative[@FunctionalRole != 1])!=0">
				<p class="center bold margin-top-small upper">
					<xsl:if test="Organization[RAFP]">Представительство (филиал) иностранного юридического лица</xsl:if>
					<xsl:if test="Organization[OGRN]">Юридическое лицо</xsl:if>
				</p>
				<xsl:apply-templates select="Organization"/>
				<xsl:for-each select="Representatives/Representative[@FunctionalRole != 1]">
					<b><xsl:call-template name="FunctionalRolesList">
							<xsl:with-param name="Code"><xsl:value-of select="@FunctionalRole"/></xsl:with-param>
					</xsl:call-template>:</b>
					<table>
						<tr><td style="width:25%">Должность:</td><td><xsl:value-of select="Position"/></td></tr>
						<tr><td>Фамилия:</td><td><xsl:value-of select="Surname"/></td></tr>
						<tr><td>Имя:</td><td><xsl:value-of select="Name"/></td></tr>
						<xsl:if test="Patronymic">
							<tr><td>Отчество:</td><td><xsl:value-of select="Patronymic"/></td></tr>	
						</xsl:if>
					</table>
				</xsl:for-each>
			</xsl:if>

			<xsl:if test="IndividualEntrepreneur[@FunctionalRole != 1]">
				<p class="center bold margin-top-small upper">Индивидуальный предприниматель</p>
				<b><xsl:call-template name="FunctionalRolesList">
					<xsl:with-param name="Code"><xsl:value-of select="IndividualEntrepreneur/@FunctionalRole"/></xsl:with-param>
				</xsl:call-template>:</b>
				<xsl:apply-templates select="IndividualEntrepreneur"/>
			</xsl:if>
			
			<xsl:if test="Person[@FunctionalRole != 1]">
				<p class="center bold margin-top-small upper">Физическое лицо</p>
				<b><xsl:call-template name="FunctionalRolesList">
					<xsl:with-param name="Code"><xsl:value-of select="Person/@FunctionalRole"/></xsl:with-param>
				</xsl:call-template>:</b>
				<xsl:apply-templates select="Person"/>
			</xsl:if>
			
		</xsl:for-each>

		<xsl:if test="count(/Document/Requisites/Authors/Author/Representatives/Representative[@FunctionalRole != 1])='0' 
					and count(/Document/Requisites/Authors/Author/IndividualEntrepreneur[@FunctionalRole != '1'])=0 
					and count(/Document/Requisites/Authors/Author/Person[@FunctionalRole != '1'])=0">
			
			<p class="center margin-top-small upper">Согласующие лица отсутствуют</p>
		</xsl:if>
		
	</xsl:template>

	<xsl:template name="ObjectMainInfo">
		<a name="ch11"/>
		<h3 class="bckgr upper">11. Общие сведения и идентификационные признаки</h3>

		<h4 class="upper under">11.1. Общие сведения и идентификационные признаки объекта:</h4>

		<table>
			<tr><td width="25%">Наименование объекта:</td><td><xsl:value-of select="/Document/Content/Object/Name"/></td></tr>
			
			<xsl:if test="/Document/Content/Object/Address">
				<tr>
					<td width="25%">Адрес объекта:</td>
					<td><xsl:apply-templates select="/Document/Content/Object/Address"/></td>
				</tr>
			</xsl:if>
			<xsl:if test="/Document/Content/Object/BeginAddress">
				<tr>
					<td width="25%">Адрес начального пункта линейного объекта:</td>
					<td><xsl:apply-templates select="/Document/Content/Object/BeginAddress"/></td>
				</tr>
				<tr>
					<td width="25%">Адрес конечного пункта линейного объекта:</td>
					<td><xsl:apply-templates select="/Document/Content/Object/FinalAddress"/></td>
				</tr>
			</xsl:if>
			<tr>
				<td>Вид объекта:</td><td>
					<xsl:apply-templates select="/Document/Content/Object/ObjectType"/>
				</td>
			</tr>
			<xsl:if test="/Document/Content/Object/@Code">
				<tr>
					<td>Код объекта:</td>
					<td colspan="3"><xsl:value-of select="/Document/Content/Object/@Code"/></td>
				</tr>
			</xsl:if>
			<tr>
				<td>Сведения об отнесении объекта к особо опасным и технически сложным объектам (номер подпункта пункта 1 статьи 48.1 Градостроительного кодекса Российской Федерации):</td>
				<td>
					<xsl:if test="/Document/Content/Object/@DangerousAndComplex">
						<xsl:call-template name="DangerousAndComplexObject">
							<xsl:with-param name="Code" select="/Document/Content/Object/@DangerousAndComplex"/>
						</xsl:call-template>
					</xsl:if>
					<xsl:if test="not(/Document/Content/Object/@DangerousAndComplex)">Не относится</xsl:if>						
				</td>
			</tr>
			<tr>
				<td>Принадлежность к категории уникальных объектов:</td>
				<td>
					<xsl:if test="/Document/Content/Object/@Unique">
						<xsl:call-template name="UniqueObject">
							<xsl:with-param name="Code" select="/Document/Content/Object/@Unique"/>
						</xsl:call-template>
					</xsl:if>
					<xsl:if test="not(/Document/Content/Object/@Unique)">Не принадлежит</xsl:if>
				</td>
			</tr>
			<tr>
				<td>Сведения о месте расположения объекта капитального строительства:</td>
				<td>
					<xsl:call-template name="Placement">
						<xsl:with-param name="Code" select="/Document/Content/Object/@Placement"/>
					</xsl:call-template>
				</td>
			</tr>
			<tr>
				<td>Принадлежность к объектам культурного наследия (памятникам истории и культуры) народов Российской Федерации:</td>
				<td>
					<xsl:if test="/Document/Content/Object/@IsCulturalHeritage='true'">Принадлежит</xsl:if>
					<xsl:if test="/Document/Content/Object/@IsCulturalHeritage='false'">Не принадлежит</xsl:if>
				</td>
			</tr>
			<tr><td colspan="2" class="upper center">Идентификационные признаки:</td></tr>
			<xsl:call-template name="ObjectIdentity">
				<xsl:with-param name="Obj" select="/Document/Content/Object"/>
			</xsl:call-template>
		</table>
		
		
		<h4 class="upper margin-top-small under">11.2. Общие сведения и идентификационные признаки объектов капитального строительства, входящих в состав:</h4>
		<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
			<xsl:with-param name="level" select="1."/>
			<xsl:with-param name="show" select="0"/>
		</xsl:apply-templates>
		
		<xsl:if test="not(/Document/Content/Object/ObjectParts)">
			<table><tr><td>Требования отсутствуют</td></tr></table>
		</xsl:if>
	
	</xsl:template>

	<xsl:template name="ObjectIdentity">
		<xsl:param name="Obj"/>
		
		<xsl:if test="$Obj/FunctionsNote">
			<tr>
				<td>Функциональное назначение объекта (неформализованное описание):</td>
				<td colspan="3"><xsl:value-of select="$Obj/FunctionsNote"/></td>
			</tr>
		</xsl:if>
		<xsl:if test="$Obj/FunctionsClass">
			<tr>
				<td>Код классификатора функционального назначения объекта:</td>
				<td colspan="3"><xsl:value-of select="$Obj/FunctionsClass"/></td>
			</tr>
		</xsl:if>
		<tr>
			<td width="25%">Принадлежность к объектам транспортной инфраструктуры и к другим объектам, функционально-технологические особенности, которых, влияют на их безопасность:</td>
			<td>
				<xsl:if test="$Obj/@SecurityInfluence = 'true'">Принадлежит</xsl:if>
				<xsl:if test="$Obj/@SecurityInfluence = 'false'">Не принадлежит</xsl:if>
				<xsl:if test="not($Obj/@SecurityInfluence)">Сведения отсутствуют</xsl:if>
			</td>
		</tr>
		<tr>
			<td>Возможность опасных природных процессов и явлений и техногенных воздействий на территории, на которой будут осуществляться строительство, реконструкция и эксплуатация объекта капитального строительства</td>
			<td>
				<xsl:if test="$Obj/@NaturalImpact = 'true'">Присутствует</xsl:if>
				<xsl:if test="$Obj/@NaturalImpact = 'false'">Отсутствует</xsl:if>
				<xsl:if test="not($Obj/@NaturalImpact)">Сведения отсутствуют</xsl:if>
			</td>
		</tr>
		<tr>
			<td>Принадлежность к опасным производственным объектам (класс опасности):</td>
			<td>
				<xsl:value-of select="$Obj/@DangerousIndustrialObject"/>
				<xsl:if test="not($Obj/@DangerousIndustrialObject)">Сведения отсутствуют</xsl:if>
			</td>
		</tr>
		<tr>
			<td>Пожарная и взрывопожарная опасность (категория опасности):</td>
			<td>
				<xsl:value-of select="$Obj/@FireDangerCategory"/>
				<xsl:if test="not($Obj/@FireDangerCategory)">Сведения отсутствуют</xsl:if>
			</td>
		</tr>
		<tr>
			<td>Наличие помещений с постоянным пребыванием людей:</td>
			<td>
				<xsl:if test="$Obj/@PeoplePermanentStay = 'true'">Да</xsl:if>
				<xsl:if test="$Obj/@PeoplePermanentStay = 'false'">Нет</xsl:if>
				<xsl:if test="not($Obj/@PeoplePermanentStay)">Сведения отсутствуют</xsl:if>
			</td>
		</tr>
		<tr>
			<td>Уровень ответственности:</td>
			<td><xsl:value-of select="$Obj/@ResponsibilityLevel"/></td>
		</tr>
	</xsl:template>

	<xsl:template name="MarginalCost">
		<a name="ch16"/>
		<h3 class="bckgr upper">16. Предполагаемая (предельная) стоимость строительства объекта</h3>
		<xsl:call-template name="TextBlockInTable">
			<xsl:with-param name="obj" select="/Document/Content/MarginalCost"></xsl:with-param>
		</xsl:call-template>		
	</xsl:template>
	
	<xsl:template name="JustificationSafety">
		<a name="ch13"/>
		<h3 class="bckgr upper">13. Требования о необходимости соответствия проектной документации обоснованию безопасности опасного производственного объекта</h3>
		<xsl:call-template name="TextBlockInTable">
			<xsl:with-param name="obj" select="/Document/Content/JustificationSafety"></xsl:with-param>
		</xsl:call-template>		
	</xsl:template>
	
	<xsl:template name="QualitySolutions">
		<a name="ch14"/>
		<h3 class="bckgr upper">14. Требования к качеству, конкурентоспособности, экологичности и энергоэффективности проектных решений</h3>
		<xsl:call-template name="TextBlockInTable">
			<xsl:with-param name="obj" select="/Document/Content/QualitySolutions"></xsl:with-param>
		</xsl:call-template>		
	</xsl:template>

	<xsl:template name="ObjectOtherRequirements">
		
		<a name="ch42"/>
		<h3 class="bckgr upper">42. Требования к подготовке сметной документации</h3>
		<h4 class="upper under">42.1 Объект капитального строительства:</h4>
		<xsl:if test="/Document/Content/Object/Estimate">
			<xsl:call-template name="TextBlockInTable">
				<xsl:with-param name="obj" select="/Document/Content/Object/Estimate"/>
			</xsl:call-template>
		</xsl:if>
		<xsl:if test="not(/Document/Content/Object/Estimate)">
			<p class="border">Требования отсутствуют</p>
		</xsl:if>
		
		<h4 class="upper under">42.2 Объекты капитального строительства, входящие в состав:</h4>
		<table><tr><td class="justify">
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="6"/>
				<xsl:with-param name="SectionName" select="'Estimate'"/>
			</xsl:apply-templates>
			<xsl:if test="not(/Document/Content/Object/ObjectParts)">
				<p>Требования отсутствуют</p>	
			</xsl:if>
		</td></tr></table>
	
		<!-- -->		
		<a name="ch43"/>
		<h3 class="bckgr upper">43. Требования к разработке специальных технических условий</h3>
		<h4 class="upper under">43.1. Объект капитального строительства:</h4>
		<xsl:if test="/Document/Content/Object/SpecialTechnicalConditions">
			<xsl:call-template name="TextBlockInTable">
				<xsl:with-param name="obj" select="/Document/Content/Object/SpecialTechnicalConditions"/>
			</xsl:call-template>
		</xsl:if>
		<xsl:if test="not(/Document/Content/Object/SpecialTechnicalConditions)">
			<p class="border">Требования отсутствуют</p>
		</xsl:if>
		
		<h4 class="upper under">43.2. Объекты капитального строительства, входящие в состав:</h4>
		<table><tr><td class="justify">
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="6"/>
				<xsl:with-param name="SectionName" select="'SpecialTechnicalConditions'"/>
			</xsl:apply-templates>
			<xsl:if test="not(/Document/Content/Object/ObjectParts)">
				<p>Требования отсутствуют</p>
			</xsl:if>
		</td></tr></table>
	
		<!-- -->		
		<a name="ch44"/>
		<h3 class="bckgr upper">44. Требования о применении при разработке проектной документации документов в области стандартизации</h3>
		<h4 class="upper under">44.1. Объект капитального строительства:</h4>
		<xsl:if test="/Document/Content/Object/Standardization">
			<xsl:call-template name="TextBlockInTable">
				<xsl:with-param name="obj" select="/Document/Content/Object/Standardization"/>
			</xsl:call-template>
		</xsl:if>
		<xsl:if test="not(/Document/Content/Object/Standardization)">
			<p class="border">Требования отсутствуют</p>
		</xsl:if>
		
		<h4 class="upper under">44.2. Объекты капитального строительства, входящие в состав:</h4>
		<table><tr><td class="justify">
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="6"/>
				<xsl:with-param name="SectionName" select="'Standardization'"/>
			</xsl:apply-templates>
			<xsl:if test="not(/Document/Content/Object/ObjectParts)">
				<p>Требования отсутствуют</p>
			</xsl:if>
		</td></tr></table>
		
		<!-- -->		
		<a name="ch45"/>
		<h3 class="bckgr upper">45. Требования к выполнению демонстрационных материалов, макетов</h3>
		<h4 class="upper under">45.1. Объект капитального строительства:</h4>
		<xsl:if test="/Document/Content/Object/Demonstration">
			<xsl:call-template name="TextBlockInTable">
				<xsl:with-param name="obj" select="/Document/Content/Object/Demonstration"/>
			</xsl:call-template>
		</xsl:if>
		<xsl:if test="not(/Document/Content/Object/Demonstration)">
			<p class="border">Требования отсутствуют</p>
		</xsl:if>
		
		<h4 class="upper under">45.2. Объекты капитального строительства, входящие в состав:</h4>
		<table><tr><td class="justify">
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="6"/>
				<xsl:with-param name="SectionName" select="'Demonstration'"/>
			</xsl:apply-templates>
			<xsl:if test="not(/Document/Content/Object/ObjectParts)">
				<p>Требования отсутствуют</p>
			</xsl:if>
		</td></tr></table>
	
		<!-- -->		
		<a name="ch46"/>
		<h3 class="bckgr upper">46. Требования о подготовке проектной документации, содержащей материалы в форме информационной модели</h3>
		<h4 class="upper under">46.1. Объект капитального строительства:</h4>
		<xsl:if test="/Document/Content/Object/InformationModel">
			<xsl:call-template name="TextBlockInTable">
				<xsl:with-param name="obj" select="/Document/Content/Object/InformationModel"/>
			</xsl:call-template>
		</xsl:if>
		<xsl:if test="not(/Document/Content/Object/InformationModel)">
			<p class="border">Требования отсутствуют</p>
		</xsl:if>
		
		<h4 class="upper under">46.2. Объекты капитального строительства, входящие в состав:</h4>
		<table><tr><td class="justify">
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="6"/>
				<xsl:with-param name="SectionName" select="'InformationModel'"/>
			</xsl:apply-templates>
			<xsl:if test="not(/Document/Content/Object/ObjectParts)">
				<p>Требования отсутствуют</p>
			</xsl:if>
		</td></tr></table>
	
		<!-- -->		
		<a name="ch47"/>
		<h3 class="bckgr upper">47. Требование о применении типовой проектной документации, типового проектного решения</h3>
		<h4 class="upper under">47.1. Объект капитального строительства:</h4>
		<xsl:if test="/Document/Content/Object/TypicalDesign">
			<xsl:call-template name="TextBlockInTable">
				<xsl:with-param name="obj" select="/Document/Content/Object/TypicalDesign"/>
			</xsl:call-template>
		</xsl:if>
		<xsl:if test="not(/Document/Content/Object/TypicalDesign)">
			<p class="border">Требования отсутствуют</p>
		</xsl:if>
		
		<h4 class="upper under">47.2. Объекты капитального строительства, входящие в состав:</h4>
		<table><tr><td class="justify">
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="6"/>
				<xsl:with-param name="SectionName" select="'TypicalDesign'"/>
			</xsl:apply-templates>
			<xsl:if test="not(/Document/Content/Object/ObjectParts)">
				<p>Требования отсутствуют</p>
			</xsl:if>
		</td></tr></table>
	
		<!-- -->		
		<a name="ch48"/>
		<h3 class="bckgr upper">48. Прочие дополнительные требования и указания, конкретизирующие объём проектных работ</h3>
		<h4 class="upper under">48.1. Объект капитального строительства:</h4>
		<xsl:if test="/Document/Content/Object/OtherRequirements">
			<xsl:call-template name="TextBlockInTable">
				<xsl:with-param name="obj" select="/Document/Content/Object/OtherRequirements"/>
			</xsl:call-template>
		</xsl:if>
		<xsl:if test="not(/Document/Content/Object/OtherRequirements)">
			<p class="border">Требования отсутствуют</p>
		</xsl:if>
		
		<h4 class="upper under">48.2. Объекты капитального строительства, входящие в состав:</h4>
		<table><tr><td class="justify">
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="6"/>
				<xsl:with-param name="SectionName" select="'OtherRequirements'"/>
			</xsl:apply-templates>
			<xsl:if test="not(/Document/Content/Object/ObjectParts)">
				<p>Требования отсутствуют</p>
			</xsl:if>
		</td></tr></table>
	</xsl:template>

	<xsl:template name="UniqueObject">
		<xsl:param name="Code" select="0"/>
		<p>Объект относится к категории уникальных в соответствии с пунктом <xsl:value-of select="$Code"/> части 2 статьи 48.1 Градостроительного кодекса Российской Федерации:</p> 
		<p>
			<xsl:choose>
				<xsl:when test="$Code=1">1) высота более чем 100 метров, для ветроэнергетических установок - более чем 250 метров</xsl:when>
				<xsl:when test="$Code=2">2) пролеты более чем 100 метров</xsl:when>
				<xsl:when test="$Code=3">3) наличие консоли более чем 20 метров</xsl:when>
				<xsl:when test="$Code=4">4) заглубление подземной части (полностью или частично) ниже планировочной отметки земли более чем на 15 метров</xsl:when>
			</xsl:choose>
		</p>
	</xsl:template>
		
	<xsl:template name="DangerousAndComplexObject">
		<xsl:param name="Code" select="0"/>
		<p>Объект относится к категории особо опасных и технически сложных объектов в соответствии с пунктом 
			<xsl:choose>
				<xsl:when test="$Code=1"> 1 </xsl:when>
				<xsl:when test="$Code=2"> 2 </xsl:when>
				<xsl:when test="$Code=3"> 3 </xsl:when>
				<xsl:when test="$Code=4"> 4 </xsl:when>
				<xsl:when test="$Code=5"> 5 </xsl:when>
				<xsl:when test="$Code=6"> 6 </xsl:when>
				<xsl:when test="$Code=7"> 7 </xsl:when>
				<xsl:when test="$Code=8"> 8 </xsl:when>
				<xsl:when test="$Code=9"> 9 </xsl:when>
				<xsl:when test="$Code=10"> 10.1 </xsl:when>
				<xsl:when test="$Code=11"> 10.2 </xsl:when>
				<xsl:when test="$Code=12"> 11. a</xsl:when>
				<xsl:when test="$Code=13"> 11. б</xsl:when>
				<xsl:when test="$Code=14"> 11. в</xsl:when>
			</xsl:choose>
			части 1 статьи 48.2 Градостроительного кодекса Российской Федерации:</p> 
		<p>
			<xsl:choose>
				<xsl:when test="$Code=1">1) объекты использования атомной энергии в соответствии с законодательством Российской Федерации об использовании атомной энергии, за исключением объектов, содержащих:<br/>
					а) только радиационные источники, в которых генерируется ионизирующее излучение, на объектах, радиационное воздействие от которых в случае аварии ограничивается помещениями, где осуществляется непосредственное обращение с источниками ионизирующего излучения;<br/>
					б) радиационные источники, содержащие в своем составе только радионуклидные источники четвертой и пятой категорий радиационной опасности в соответствии с законодательством Российской Федерации об использовании атомной энергии </xsl:when>
				<xsl:when test="$Code=2">2) гидротехнические сооружения первого и второго классов, устанавливаемые в соответствии с законодательством о безопасности гидротехнических сооружений</xsl:when>
				<xsl:when test="$Code=3">3) сооружения связи, являющиеся особо опасными, технически сложными в соответствии с законодательством Российской Федерации в области связи</xsl:when>
				<xsl:when test="$Code=4">4) линии электропередачи и иные объекты электросетевого хозяйства напряжением 330 киловольт и более</xsl:when>
				<xsl:when test="$Code=5">5) объекты космической инфраструктуры</xsl:when>
				<xsl:when test="$Code=6">6) объекты инфраструктуры воздушного транспорта, являющиеся особо опасными, технически сложными объектами в соответствии с воздушным законодательством Российской Федерации</xsl:when>
				<xsl:when test="$Code=7">7) объекты капитального строительства инфраструктуры железнодорожного транспорта общего пользования, являющиеся особо опасными, технически сложными объектами в соответствии с законодательством Российской Федерации о железнодорожном транспорте</xsl:when>
				<xsl:when test="$Code=8">8) объекты инфраструктуры внеуличного транспорта</xsl:when>
				<xsl:when test="$Code=9">9) портовые гидротехнические сооружения, относящиеся к объектам инфраструктуры морского порта, за исключением объектов инфраструктуры морского порта, предназначенных для стоянок и обслуживания маломерных, спортивных парусных и прогулочных судов</xsl:when>
				<xsl:when test="$Code=10">10.1) тепловые электростанции мощностью 150 мегаватт и выше</xsl:when>
				<xsl:when test="$Code=11">10.2) подвесные канатные дороги</xsl:when>
				<xsl:when test="$Code=12">11. а) опасные производственные объекты I и II классов опасности, на которых получаются, используются, перерабатываются, образуются, хранятся, транспортируются, уничтожаются опасные вещества</xsl:when>
				<xsl:when test="$Code=13">11. б) опасные производственные объекты, на которых получаются, транспортируются, используются расплавы черных и цветных металлов, сплавы на основе этих расплавов с применением оборудования, рассчитанного на максимальное количество расплава 500 килограммов и более</xsl:when>
				<xsl:when test="$Code=14">11. в) опасные производственные объекты, на которых ведутся горные работы (за исключением добычи общераспространенных полезных ископаемых и разработки россыпных месторождений полезных ископаемых, осуществляемых открытым способом без применения взрывных работ), работы по обогащению полезных ископаемых</xsl:when>
			</xsl:choose>
		</p>
	</xsl:template>

	<xsl:template name="DecisionDocuments">
		<a name="ch2"/>
		<h3 class="bckgr upper">2. Основание для проектирования объекта</h3>
		
		<table>
			<xsl:if test="count(/Document/Content/DecisionDocuments/DocumentInfo[File]) > 0">
				<thead>
					<tr>
						<th width="5%">№ п/п</th>
						<th width="65%">Наименование и реквизиты документа</th>
						<th width="25%">Наименование<br/>файла документа<br/>(подписи к файлу)</th>
						<th>Контрольная сумма файла</th>
					</tr>
				</thead>
			</xsl:if>
			<tbody>
				<xsl:for-each select="/Document/Content/DecisionDocuments/DocumentInfo">
					<xsl:sort select="@Type"/>
					<xsl:call-template name="DocumentFilesTable"/>
				</xsl:for-each>
			</tbody>
		</table>
		
		<xsl:if test="/Document/Content/DecisionDocuments/Note">
			<p class="upper bold under">Дополнительные сведения:</p>
			<table><tr><td><xsl:value-of select="/Document/Content/DecisionDocuments/Note"/></td></tr></table>
		</xsl:if>
		
	</xsl:template>

	<xsl:template name="DocumentFilesTable">
		<xsl:param name="Pos" select="position()"/>
		
		<xsl:variable name="FileNumber">
			<xsl:if test="IULFile">
				<xsl:value-of select="count(IULFile)+ count(IULFile/SignFile) + 1 + count(File) + count(File/SignFile)"/>
			</xsl:if>
			<xsl:if test="not(IULFile)">
				<xsl:value-of select="count(File) + count(File/SignFile)"/>
			</xsl:if>
		</xsl:variable>
		<xsl:variable name="IULNumber" select="count(IULFile)"/>
		
		<xsl:if test="$FileNumber!=0">
			<xsl:for-each select="File">
				<tr>
					<xsl:if test="position() = 1">
						<td>
							<xsl:if test="$FileNumber != 1">
								<xsl:attribute name="rowspan">
									<xsl:value-of select="$FileNumber"/>
								</xsl:attribute>
							</xsl:if>
							<xsl:number value="$Pos"/>.
						</td>
						<td>
							<xsl:if test="$FileNumber != 1">
								<xsl:attribute name="rowspan">
									<xsl:value-of select="$FileNumber"/>
								</xsl:attribute>
							</xsl:if>
							<a>
								<xsl:attribute name="name">
									<xsl:value-of select="../@Id"/>
								</xsl:attribute>
							</a>
							<xsl:apply-templates select=".."/>
						</td>
					</xsl:if>
					<td>
						<xsl:value-of select="Name"/>
					</td>
					<td class="center">
						<xsl:value-of select="Checksum"/>
					</td>
				</tr>
				<xsl:for-each select="SignFile">
					<tr>
						<td class="italic">
							<xsl:value-of select="Name"/>
						</td>
						<td class="center italic">
							<xsl:value-of select="Checksum"/>
						</td>
					</tr>
				</xsl:for-each>
			</xsl:for-each>
			<xsl:for-each select="IULFile">
				<xsl:if test="position() = 1">
					<tr>
						<td colspan="2">
							<xsl:if test="$IULNumber=1">Информационный удостоверяющий лист:</xsl:if>
							<xsl:if test="$IULNumber!=1">Информационные удостоверяющие листы:</xsl:if>
						</td>
					</tr>
				</xsl:if>
				<tr>
					<td>
						<xsl:value-of select="Name"/>
					</td>
					<td class="center">
						<xsl:value-of select="Checksum"/>
					</td>
				</tr>
				<xsl:for-each select="SignFile">
					<tr>
						<td class="italic">
							<xsl:value-of select="Name"/>
						</td>
						<td class="center italic">
							<xsl:value-of select="Checksum"/>
						</td>
					</tr>
				</xsl:for-each>
			</xsl:for-each>
		</xsl:if>
		
		<xsl:if test="$FileNumber=0 and ReferenceToDocumentId">
			<tr>
				<td><xsl:number value="$Pos"/>.</td>
				<td>
					<a>
						<xsl:attribute name="name">
							<xsl:value-of select="@Id"/>
						</xsl:attribute>
					</a>
					<xsl:apply-templates select="."/>
				</td>
				<td colspan="2">
					Содержится в составе документа: <br/>
					<xsl:for-each select="key('DocumentsInfoById',ReferenceToDocumentId)">
						<a class="italic">
							<xsl:attribute name="href">#<xsl:value-of select="@Id"/></xsl:attribute>
							<xsl:value-of select="Name"/>
							<xsl:if test="Changes"><xsl:text> </xsl:text>(<xsl:value-of select="Changes"/>)</xsl:if>
							<xsl:text> от </xsl:text>
							<xsl:apply-templates select="Date"/>
							<xsl:text> № </xsl:text>
							<xsl:value-of select="Number"/>
							
						</a>
					</xsl:for-each>
				</td>
			</tr>
		</xsl:if>
		<xsl:if test="$FileNumber=0 and WebLink">
			<tr>
				<td><xsl:number value="$Pos"/>.</td>
				<td>
					<a>
						<xsl:attribute name="name">
							<xsl:value-of select="@Id"/>
						</xsl:attribute>
					</a>
					<xsl:apply-templates select="."/></td>
				<td colspan="2">
					Документ опубликован:<br/>
					<a target="_blank">
						<xsl:attribute name="href">
							<xsl:value-of select="WebLink"/>
						</xsl:attribute>
						<xsl:value-of select="WebLink"/>
					</a>
				</td>
			</tr>
		</xsl:if>
	</xsl:template>
	
	<xsl:template match="DocumentInfo">
		
		<p class="margin-vertical"><b>Наименование: </b> <xsl:value-of select="Name"/><xsl:if test="Changes != ''"> (<xsl:value-of select="Changes"/>) </xsl:if></p>
		<p class="margin-vertical"><b>Номер: </b> <xsl:value-of select="Number"/></p>
		<p class="margin-vertical"><b>Дата: </b> <xsl:apply-templates select="Date"/></p>
		<p class="margin-vertical"><b>Вид: </b>
		<xsl:call-template name="DocumentTypeList">
			<xsl:with-param name="Code" select="@Type"/>
		</xsl:call-template></p>
		<p class="margin-vertical"><b>Автор: </b>
			<xsl:if test="AuthorNote"><xsl:value-of select="AuthorNote"/></xsl:if></p>
		<xsl:if test="Author">
			<xsl:apply-templates select="Author/Organization">
				<xsl:with-param name="ShowType">1</xsl:with-param>
			</xsl:apply-templates>
			<xsl:apply-templates select="Author/IndividualEntrepreneur">
				<xsl:with-param name="ShowType">1</xsl:with-param>
			</xsl:apply-templates>
			<xsl:apply-templates select="Author/Person">
				<xsl:with-param name="ShowType">1</xsl:with-param>
			</xsl:apply-templates>
		</xsl:if>

	</xsl:template>

	<xsl:template match="FinanceSources">
		<a name="ch8"/>
		<h3 class="bckgr upper">8. Источник финансирования строительства объекта</h3>
		<table>
			<thead>
				<tr>
					<td width="20%">
						Источник финансирования
						<xsl:if test="Note">
							<sup>*</sup>
						</xsl:if>
					</td>
					<td width="50%">Наименование уровня бюджета / Сведения о владельце средств</td>
					<td width="10%">Доля<br/>финанси-<br/>рования, %</td>
					<td>Примечание</td>
				</tr>
			</thead>
			<tbody>
				<xsl:for-each select="Budget">
					<tr>
						<td>Бюджетные средства</td>
						<td><xsl:apply-templates select="Level"/></td>
						<td class="center">
							<xsl:value-of select="Ratio"/>
							<xsl:if test="not(Ratio)">Сведения отсутствуют</xsl:if>
						</td>
						<td>
							<xsl:if test="not(Note)"><xsl:attribute name="class">center</xsl:attribute>-</xsl:if>
							<xsl:value-of select="Note"/>
						</td>
					</tr>
				</xsl:for-each>
				
				<xsl:for-each select="StateCustomer">
					<tr>
						<td>Средства юридических лиц, перечисленных в части 2 статьи 8.3 Градостроительного кодекса Российской Федерации</td>
						<td>
							<xsl:apply-templates select="Organization|IndividualEntrepreneur|Person">
								<xsl:with-param name="ShowType">1</xsl:with-param>
							</xsl:apply-templates>
						</td>
						<td class="center">
							<xsl:value-of select="Ratio"/>
							<xsl:if test="not(Ratio)"><text>Сведения отсутствуют</text></xsl:if>
						</td>
						<td>
							<xsl:if test="not(Note)"><xsl:attribute name="class">center</xsl:attribute>-</xsl:if>
							<xsl:value-of select="Note"/>
						</td>
					</tr>
				</xsl:for-each>
				
				<xsl:for-each select="Private">
					<tr>
						<td>Средства, не входящие в перечень, указанный в части 2 статьи 8.3 Градостроительного кодекса Российской Федерации</td>
						<td>
							<xsl:apply-templates select="Organization|IndividualEntrepreneur|Person">
								<xsl:with-param name="ShowType">1</xsl:with-param>
							</xsl:apply-templates>
						</td>
						<td class="center">
							<xsl:value-of select="Ratio"/>
							<xsl:if test="not(Ratio)">Сведения отсутствуют</xsl:if>
						</td>
						<td>
							<xsl:if test="not(Note)"><xsl:attribute name="class">center</xsl:attribute>-</xsl:if>
							<xsl:value-of select="Note"/>
						</td>
					</tr>
				</xsl:for-each>
			</tbody>
		</table>                     
		<xsl:if test="Note">
			<xsl:call-template name="StringReplaceComment">
				<xsl:with-param name="input" select="Note"/>
				<xsl:with-param name="count" select="1"/>
				<xsl:with-param name="first" select="1"/>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>	
		
	<xsl:template name="Placement">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code='1'">Объекты, расположенные на суше</xsl:when>
			<xsl:when test="$Code='2'">Водный объект</xsl:when>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="Objective">
		<a name="ch1"/>
		<h3 class="bckgr upper">1. Цель реализации проекта</h3>
		
		<xsl:call-template name="TextBlockInTable">
			<xsl:with-param name="obj" select="/Document/Content/Objective"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template name="Developers">
		<a name="ch3"/>
		<h3 class="bckgr upper">3. Застройщик</h3>
		
		<xsl:for-each select="/Document/Content/Developers/*">
			<xsl:apply-templates select=".">
				<xsl:with-param name="ShowType" select="1"/>
			</xsl:apply-templates>
		</xsl:for-each>
		
		<xsl:if test="not(/Document/Content/Developers)">
			<table><tr><td>Отсутствует</td></tr></table>
		</xsl:if>
		
	</xsl:template>

	<xsl:template name="TechnicalCustomer">
		<a name="ch4"/>
		<h3 class="bckgr upper">4. Технический заказчик</h3>
		
		<xsl:for-each select="/Document/Content/TechnicalCustomer">
			<xsl:apply-templates select="Organization">
				<xsl:with-param name="ShowType" select="1"/>
				<xsl:with-param name="ShowSRO" select="1"/>
			</xsl:apply-templates>
		</xsl:for-each>
		
		<xsl:if test="not(/Document/Content/TechnicalCustomer)">
			<table><tr><td>Отсутствует</td></tr></table>
		</xsl:if>
	</xsl:template>

	<xsl:template match="Designers">
		<a name="ch5"/>
		<h3 class="bckgr upper">5. Разработчик проектной документации</h3>

		<xsl:for-each select="Designer[@IsGeneral='true']">
			<h4 class="upper under">Генеральный разработчик проектной документации:</h4>
			<xsl:apply-templates select="Organization|IndividualEntrepreneur">
				<xsl:with-param name="ShowType" select="1"/>
				<xsl:with-param name="ShowSRO" select="1"/>
			</xsl:apply-templates>
		</xsl:for-each>
		
		<xsl:for-each select="Designer[@IsGeneral='false']">
			<xsl:if test="position()=1">
				<h4 class="upper under">Субподрядные разработчики проектной документации:</h4>
			</xsl:if>			
			<xsl:apply-templates select="Organization|IndividualEntrepreneur">
				<xsl:with-param name="ShowType" select="1"/>
				<xsl:with-param name="ShowSRO" select="1"/>
			</xsl:apply-templates>
		</xsl:for-each>
		
		<xsl:if test="Requirements">
			<h4 class="upper under">Требования к разработчикам проектной документации:</h4>
			<table>
				<thead>
					<tr class="center bold"><th width="5%">№ п/п</th><th>Требование</th></tr>
				</thead>
				<tbody>
					<xsl:for-each select="Requirements/Requirement">
						<tr><td><xsl:number value="position()" format="1. "/></td><td><xsl:value-of select="."/></td></tr>
					</xsl:for-each>
				</tbody>
			</table>
		</xsl:if>
	</xsl:template>
		
	<xsl:template match="SROMembership">
		<tr><td colspan="2" class="italic upper">Членство в СРО:</td></tr>
		<xsl:for-each select="SRO">
			<tr><td width="25%"><xsl:value-of select="@SROType"/></td><td><xsl:value-of select="."/></td></tr>
		</xsl:for-each>
	</xsl:template>
		
	<xsl:template name="Specifications">
		<a name="ch9"/>
		<h3 class="bckgr upper">9. Технические условия на подключение (присоединение) объекта к сетям инженерно-технического обеспечения</h3>
		
		<xsl:if test="count(/Document/Content/InitialDocuments/DocumentInfo[File][@Type &gt; '04.00'][@Type &lt; '05.00']) > 0">
			<table>
				<thead>
					<tr>
						<td width="5%">№ п/п</td>
						<td width="65%">Наименование и реквизиты документа</td>
						<td width="25%">Наименование<br/>файла документа<br/>(подписи к файлу)</td>
						<td>Контрольная сумма файла</td>
					</tr>
				</thead>
				<tbody>
					<xsl:for-each select="/Document/Content/InitialDocuments/DocumentInfo[File][@Type &gt; '04.00'][@Type &lt; '05.00']">
						<xsl:sort select="@Type"/>
						<xsl:call-template name="DocumentFilesTable"/>
					</xsl:for-each>
				</tbody>
			</table>			
		</xsl:if>
		<xsl:if test="count(/Document/Content/InitialDocuments/DocumentInfo[File][@Type &gt; '04.00'][@Type &lt; '05.00']) = 0">
			<table><tr><td>Отсутствуют</td></tr></table>
		</xsl:if>
	</xsl:template>	
	
	<xsl:template name="ConstructionTypeDates">
		<a name="ch6"/>
		<h3 class="bckgr upper">6. Вид и срок строительства объекта</h3>
		<h4 class="upper under">6.1. Объект капитального строительства:</h4>
		<table>
			<tr>
				<td width="50%">Вид работ:</td>
				<td>
					<xsl:apply-templates select="/Document/Content/Object/ConstructionType"/>
				</td>
			</tr>
			<tr>
				<td>Срок начала строительства объекта:</td>
				<td>
					<xsl:call-template name="FormatDate">
						<xsl:with-param name="DateTimeStr" select="/Document/Content/Object/@BeginDate"/>
					</xsl:call-template>
				</td>
			</tr>
			<tr>
				<td>Срок окончания строительства объекта:</td>
				<td>
					<xsl:call-template name="FormatDate">
						<xsl:with-param name="DateTimeStr" select="/Document/Content/Object/@EndDate"/>
					</xsl:call-template>
				</td>
			</tr>
			<tr>
				<td>Срок ввода объекта в эксплуатацию:</td>
				<td>
					<xsl:call-template name="FormatDate">
						<xsl:with-param name="DateTimeStr" select="/Document/Content/Object/@OperationDate"/>
					</xsl:call-template>
					<xsl:if test="not(/Document/Content/Object/@OperationDate)">
						Сведения отсутствуют
					</xsl:if>
				</td>
			</tr>
		</table>
		
		<h4 class="upper under">6.2. Объекты капитального строительства, входящие в состав:</h4>
		<xsl:choose>
			<xsl:when test="/Document/Content/Object/ObjectParts//*[@BeginDate or @EndDate or @OperationDate or ObjectType]">
				<table><tr><td class="justify">
					<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
						<xsl:with-param name="level" select="1."/>
						<xsl:with-param name="show" select="4"/>
					</xsl:apply-templates>
				</td></tr></table>
			</xsl:when>
			<xsl:otherwise>
				<p class="border">Требования отсутствуют</p>			
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="DesignPhases">
		<a name="ch12"/>
		<h3 class="bckgr upper">12. Стадийность проектирования и задачи</h3>
		<table>
			<thead>
				<tr class="center bold"><th width="5%">№ п/п</th><th>Наименование стадии проектирования / Задача проектирования</th></tr>
			</thead>
			<tbody>
				<xsl:for-each select="/Document/Content/DesignPhases/DesignPhase">
					<tr class="bold">
						<td colspan="2">
							<xsl:call-template name="StagesList">
								<xsl:with-param name="Code"><xsl:value-of select="@Phase"/></xsl:with-param>
							</xsl:call-template>
							<xsl:if test="Task">:</xsl:if>
						</td>
					</tr>
					<xsl:for-each select="Task">
						<tr>
							<td><xsl:number value="position()" format="1. "/></td>
							<td><xsl:value-of select="."/></td>
						</tr>
					</xsl:for-each>
				</xsl:for-each>
			</tbody>
		</table>
		<xsl:if test="Note">
			<p class="upper bold under">Дополнительные требования:</p>
			<table>
				<tr><td><xsl:value-of select="Note"/></td></tr>
			</table>
		</xsl:if>
	</xsl:template>	

	<xsl:template name="CommissioningConditions">
		<a name="ch17"/>
		<h3 class="bckgr upper">17. Условия ввода в эксплуатацию</h3>
		
		<h4 class="upper under">17.1. Объект капитального строительства:</h4>
		
		<table><tr><td class="justify">
			<xsl:choose>
				<xsl:when test="/Document/Content/Object/CommissioningConditions">
					<xsl:value-of select="/Document/Content/Object/CommissioningConditions"/>		
				</xsl:when>
				<xsl:otherwise>
					<p>Требования отсутствуют</p>
				</xsl:otherwise>
			</xsl:choose>
		</td></tr></table>
			
		<h4 class="upper under">17.2. Объекты капитального строительства, входящие в состав:</h4>
		
		<xsl:choose>
			<xsl:when test="/Document/Content/Object/ObjectParts">
				<table><tr><td class="justify">
					<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
						<xsl:with-param name="level" select="1."/>
						<xsl:with-param name="show" select="3"/>
					</xsl:apply-templates>
				</td></tr></table>
			</xsl:when>
			<xsl:otherwise>
				<p class="border">Требования отсутствуют</p>			
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>	
	
	<xsl:template match="ObjectParts">
		<xsl:param name="level"/>
		<xsl:param name="show"/>
		<xsl:param name="SectionName"/>
		
		<xsl:for-each select="Complex">
			<p class="bold upper margin-top-small pad-left bckgr-list">
				<xsl:value-of select="$level"/>.<xsl:number value="position()" format="1. "/>
				<xsl:value-of select="Name"/>
			</p>
			<xsl:apply-templates select=".">
				<xsl:with-param name="show" select="$show"/>
			</xsl:apply-templates>
			<xsl:apply-templates select="ObjectParts">
				<xsl:with-param name="level" select="concat($level,'.',position())"></xsl:with-param>
				<xsl:with-param name="show" select="$show"/>
				<xsl:with-param name="SectionName" select="$SectionName"/>
			</xsl:apply-templates>
		</xsl:for-each>
		
		<xsl:for-each select="OKS">
			<p class="bold upper margin-top-small pad-left bckgr-list">
				<xsl:value-of select="$level"/>.<xsl:number value="position()+count(../Complex)" format="1. "/>
				<xsl:value-of select="Name"/>
			</p>
			<xsl:apply-templates select=".">
				<xsl:with-param name="show" select="$show"/>
				<xsl:with-param name="level" select="$level"/>
				<xsl:with-param name="SectionName" select="$SectionName"/>
			</xsl:apply-templates>
		</xsl:for-each>
	</xsl:template>
	
	<xsl:template match="Complex">
		<xsl:param name="show"/>
		
		<xsl:if test="$show=0">
			<table>
				<tr>
					<td width="25%">Наименование составной части - сложного объекта капитального строительства (состоящего из двух и более объектов капитального строительства):</td>
					<td colspan="3"><xsl:value-of select="Name"/></td>
				</tr>
				<xsl:if test="Address">
					<tr>
						<td>Почтовый (строительный) адрес (местоположение):</td>
						<td><xsl:apply-templates select="Address"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="BeginAddress">
					<tr>
						<td>Адрес начального пункта линейного объекта:</td>
						<td><xsl:apply-templates select="BeginAddress"/></td>
					</tr>
					<tr>
						<td>Адрес конечного пункта линейного объекта:</td>
						<td><xsl:apply-templates select="FinalAddress"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="ObjectType">
					<tr>
						<td>Вид объекта капитального строительства:</td>
						<td colspan="3"><xsl:apply-templates select="ObjectType"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="ConstructionType">
					<tr>
						<td>Вид строительных работ:</td>
						<td colspan="3"><xsl:apply-templates select="ConstructionType"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="@Code">
					<tr>
						<td>Код объекта капитального строительства:</td>
						<td colspan="3"><xsl:value-of select="@Code"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="FunctionsNote">
					<tr>
						<td>Функциональное назначение объекта капитального строительства (неформализованное описание):</td>
						<td colspan="3"><xsl:value-of select="FunctionsNote"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="FunctionsClass">
					<tr>
						<td>Код классификатора функционального назначения объекта капитального строительства</td>
						<td colspan="3"><xsl:value-of select="FunctionsClass"/></td>
					</tr>
				</xsl:if>
				<tr>
					<td width="25%">Принадлежность к объектам транспортной инфраструктуры и к другим объектам, функционально-технологические особенности, которых, влияют на их безопасность:</td>
					<td>
						<xsl:if test="@SecurityInfluence = 'true'">Принадлежит</xsl:if>
						<xsl:if test="@SecurityInfluence = 'false'">Не принадлежит</xsl:if>
					</td>
				</tr>
				<tr>
					<td>Принадлежность к опасным производственным объектам (класс опасности):</td>
					<td><xsl:value-of select="@DangerousIndustrialObject"/></td>
				</tr>
			</table>
		</xsl:if>
		<xsl:if test="$show=1">
			<xsl:if test="POI">
				<xsl:call-template name="POITEI">
					<xsl:with-param name="Obj" select="POI"/>
				</xsl:call-template>	
			</xsl:if>
			<xsl:if test="TEI">
				<xsl:call-template name="POITEI">
					<xsl:with-param name="Obj" select="TEI"/>
				</xsl:call-template>
			</xsl:if>
		</xsl:if>
	</xsl:template>	
		
	<xsl:template match="OKS">
		<xsl:param name="show"/>
		<xsl:param name="level" select="0"/>
		<xsl:param name="SectionName" select="0"/>
		
		<xsl:if test="$show=0">
			<table>
				<tr>
					<td width="25%">Наименование объекта капитального строительства, входящего в состав сложного объекта</td>
					<td colspan="3"><xsl:value-of select="Name"/></td>
				</tr>
				<xsl:if test="Address">
					<tr>
						<td>Почтовый (строительный) адрес (местоположение) объекта капитального строительства:</td>
						<td><xsl:apply-templates select="Address"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="BeginAddress">
					<tr>
						<td>Адрес начального пункта линейного объекта:</td>
						<td><xsl:apply-templates select="BeginAddress"/></td>
					</tr>
					<tr>
						<td>Адрес конечного пункта линейного объекта:</td>
						<td><xsl:apply-templates select="FinalAddress"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="ObjectType">
					<tr>
						<td>Вид объекта капитального строительства:</td>
						<td colspan="3"><xsl:apply-templates select="ObjectType"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="ConstructionType">
					<tr>
						<td>Вид строительных работ:</td>
						<td colspan="3"><xsl:apply-templates select="ConstructionType"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="@Code">
					<tr>
						<td>Код объекта капитального строительства:</td>
						<td colspan="3"><xsl:value-of select="@Code"/></td>
					</tr>
				</xsl:if>
				<tr>
					<td>Сведения об отнесении объекта к особо опасным и технически сложным объектам (номер подпункта пункта 1 статьи 48.1 Градостроительного кодекса Российской Федерации):</td>
					<td>
						<xsl:if test="@DangerousAndComplex">
							<xsl:call-template name="DangerousAndComplexObject">
								<xsl:with-param name="Code" select="@DangerousAndComplex"/>
							</xsl:call-template>
						</xsl:if>
						<xsl:if test="not(@DangerousAndComplex)">Не относится</xsl:if>						
					</td>
				</tr>
				<tr>
					<td>Принадлежность к категории уникальных объектов:</td>
					<td>
						<xsl:if test="@Unique">
							<xsl:call-template name="UniqueObject">
								<xsl:with-param name="Code" select="@Unique"/>
							</xsl:call-template>
						</xsl:if>
						<xsl:if test="not(@Unique)">Не принадлежит</xsl:if>
					</td>
				</tr>
				<tr>
					<td>Сведения о месте расположения объекта капитального строительства:</td>
					<td>
						<xsl:call-template name="Placement">
							<xsl:with-param name="Code" select="@Placement"/>
						</xsl:call-template>
					</td>
				</tr>
				<tr>
					<td>Принадлежность к объектам культурного наследия (памятникам истории и культуры) народов Российской Федерации:</td>
					<td>
						<xsl:if test="@IsCulturalHeritage='true'">Принадлежит</xsl:if>
						<xsl:if test="@IsCulturalHeritage='false'">Не принадлежит</xsl:if>
					</td>
				</tr>
				<tr><td colspan="2" class="upper center">Идентификационные признаки:</td></tr>
				<xsl:call-template name="ObjectIdentity">
					<xsl:with-param name="Obj" select="."/>
				</xsl:call-template>
			</table>
		</xsl:if>
		<xsl:if test="$show=1">
			<xsl:if test="POI">
				<xsl:call-template name="POITEI">
					<xsl:with-param name="Obj" select="POI"/>
				</xsl:call-template>	
			</xsl:if>
			<xsl:if test="TEI">
				<xsl:call-template name="POITEI">
					<xsl:with-param name="Obj" select="TEI"/>
				</xsl:call-template>	
			</xsl:if>
		</xsl:if>
		<xsl:if test="$show=2">
			<xsl:for-each select="ProjectSolutions">
				<xsl:choose>
					<xsl:when test="$SectionName='SchemePlanningOrganizationLand'">
						<xsl:apply-templates select="SchemePlanningOrganizationLand/Requirements"/>
						<xsl:apply-templates select="SchemePlanningOrganizationLand/ComponentRequirements"/>
						<xsl:if test="not(SchemePlanningOrganizationLand)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='RightOfWayProject'">
						<xsl:apply-templates select="RightOfWayProject/Requirements"/>
						<xsl:apply-templates select="RightOfWayProject/ComponentRequirements"/>
						<xsl:if test="not(RightOfWayProject)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='ArchitectSolutions'">
						<xsl:apply-templates select="ArchitectSolutions/Zones"/>
						<xsl:apply-templates select="ArchitectSolutions/Requirements"/>
						<xsl:apply-templates select="ArchitectSolutions/ComponentRequirements"/>
						<xsl:if test="not(ArchitectSolutions)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='TechnologicalSolutions'">
						<xsl:apply-templates select="TechnologicalSolutions/Requirements"/>
						<xsl:apply-templates select="TechnologicalSolutions/ComponentRequirements"/>
						<xsl:if test="not(TechnologicalSolutions)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='StructuralSpacePlanningSolutions'">
						
						<xsl:for-each select="StructuralSpacePlanningSolutions/Section">
							<p class="bold upper">
								<xsl:call-template name="StructuralSpacePlanningSolutionsSectionsName">
									<xsl:with-param name="Name" select="@Name"/>
								</xsl:call-template>:
							</p>
							<xsl:apply-templates select="Requirements"/>
							<xsl:apply-templates select="ComponentRequirements"/>
						</xsl:for-each>
						
						<xsl:if test="not(StructuralSpacePlanningSolutions)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='TechnologicalConstructiveSolutions'">
						<xsl:apply-templates select="TechnologicalConstructiveSolutions/Requirements"/>
						<xsl:apply-templates select="TechnologicalConstructiveSolutions/ComponentRequirements"/>
						<xsl:if test="not(TechnologicalConstructiveSolutions)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='InfrastructureLinearObject'">
						<xsl:apply-templates select="InfrastructureLinearObject/Requirements"/>
						<xsl:apply-templates select="InfrastructureLinearObject/ComponentRequirements"/>
						<xsl:if test="not(InfrastructureLinearObject)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='EngineeringTechnicalSolutions'">
						
						<xsl:if test="EngineeringTechnicalSolutions">
							<h4 class="under upper">Требования к основному технологическому оборудованию:</h4>
							<xsl:for-each select="EngineeringTechnicalSolutions/TechnologicalEquipment">
								<p class="upper under pad-left bold">
									<xsl:call-template name="EngineeringTechnicalSystemsName">
										<xsl:with-param name="Name" select="@Name"/>
									</xsl:call-template>:
								</p>
								<xsl:apply-templates select="Requirements"/>
								<xsl:apply-templates select="ComponentRequirements"/>
							</xsl:for-each>
							<xsl:if test="not(EngineeringTechnicalSolutions/TechnologicalEquipment)"><p class="border">Требования отсутствуют</p></xsl:if>
							
							<h4 class="under upper">Требования к наружным сетям инженерно-технического обеспечения, точкам присоединения:</h4>
							
							<xsl:for-each select="EngineeringTechnicalSolutions/ExternalEngineeringNetwork">
								<p class="bold upper">
									<xsl:call-template name="EngineeringTechnicalSystemsName">
										<xsl:with-param name="Name" select="@Name"/>
									</xsl:call-template>:
								</p>
								<xsl:apply-templates select="Requirements"/>
								<xsl:apply-templates select="ComponentRequirements"/>
							</xsl:for-each>
							<xsl:if test="not(EngineeringTechnicalSolutions/ExternalEngineeringNetwork)"><p class="border">Требования отсутствуют</p></xsl:if>
						</xsl:if>
						
						<xsl:if test="not(EngineeringTechnicalSolutions)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='EnvironmentalProtection'">
						<xsl:apply-templates select="EnvironmentalProtection/Requirements"/>
						<xsl:apply-templates select="EnvironmentalProtection/ComponentRequirements"/>
						<xsl:if test="not(EnvironmentalProtection)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='FireSafetyMeasures'">
						<xsl:apply-templates select="FireSafetyMeasures/Requirements"/>
						<xsl:apply-templates select="FireSafetyMeasures/ComponentRequirements"/>
						<xsl:if test="not(FireSafetyMeasures)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='EnergyEfficiencyRequirements'">
						<xsl:apply-templates select="EnergyEfficiencyRequirements/Requirements"/>
						<xsl:apply-templates select="EnergyEfficiencyRequirements/ComponentRequirements"/>
						<xsl:if test="not(EnergyEfficiencyRequirements)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='LowMobilityGroupsPopulation'">
						<xsl:apply-templates select="LowMobilityGroupsPopulation/Requirements"/>
						<xsl:apply-templates select="LowMobilityGroupsPopulation/ComponentRequirements"/>
						<xsl:if test="not(LowMobilityGroupsPopulation)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='EngineeringTechnicalStrengthening'">
						<xsl:apply-templates select="EngineeringTechnicalStrengthening/Requirements"/>
						<xsl:apply-templates select="EngineeringTechnicalStrengthening/ComponentRequirements"/>
						<xsl:if test="not(EngineeringTechnicalStrengthening)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='SafeLivingConditions'">
						<xsl:apply-templates select="SafeLivingConditions/Requirements"/>
						<xsl:apply-templates select="SafeLivingConditions/ComponentRequirements"/>
						<xsl:if test="not(SafeLivingConditions)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='TechnicalOperation'">
						<xsl:apply-templates select="TechnicalOperation/Requirements"/>
						<xsl:apply-templates select="TechnicalOperation/ComponentRequirements"/>
						<xsl:if test="not(TechnicalOperation)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='ConstructionOrganizationProject'">
						<xsl:apply-templates select="ConstructionOrganizationProject/Requirements"/>
						<xsl:apply-templates select="ConstructionOrganizationProject/ComponentRequirements"/>
						<xsl:if test="not(ConstructionOrganizationProject)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='DemolishPreserveBuildings'">
						<xsl:apply-templates select="DemolishPreserveBuildings/Requirements"/>
						<xsl:apply-templates select="DemolishPreserveBuildings/ComponentRequirements"/>
						<xsl:if test="not(DemolishPreserveBuildings)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='Landscaping'">
						<xsl:apply-templates select="Landscaping/Requirements"/>
						<xsl:apply-templates select="Landscaping/ComponentRequirements"/>
						<xsl:if test="not(Landscaping)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='LandReclamationProject'">
						<xsl:apply-templates select="LandReclamationProject/Requirements"/>
						<xsl:apply-templates select="LandReclamationProject/ComponentRequirements"/>
						<xsl:if test="not(LandReclamationProject)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='StorageLocations'">
						<xsl:apply-templates select="StorageLocations/Requirements"/>
						<xsl:apply-templates select="StorageLocations/ComponentRequirements"/>
						<xsl:if test="not(StorageLocations)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='ResearchDevelopmentWork'">
						<xsl:apply-templates select="ResearchDevelopmentWork/Requirements"/>
						<xsl:apply-templates select="ResearchDevelopmentWork/ComponentRequirements"/>
						<xsl:if test="not(ResearchDevelopmentWork)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:when test="$SectionName='Other'">
						<xsl:apply-templates select="Other/Requirements"/>
						<xsl:apply-templates select="Other/ComponentRequirements"/>
						<xsl:if test="not(Other)"><p class="border">Требования отсутствуют</p></xsl:if>
					</xsl:when>
					<xsl:otherwise>
						<p class="border">Требования отсутствуют</p>
					</xsl:otherwise>
				</xsl:choose>	
			</xsl:for-each>
			<xsl:if test="not(ProjectSolutions)">
				<p class="border">Требования отсутствуют</p>
			</xsl:if>
		</xsl:if>
		<xsl:if test="$show=3">
			<p class="border"><xsl:value-of select="CommissioningConditions"/></p>
		</xsl:if>
		<xsl:if test="$show=4">
			<table>
				<xsl:if test="ConstructionType">
					<tr>
						<td width="50%">Вид работ:</td>
						<td><xsl:apply-templates select="ConstructionType"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="@BeginDate">
					<tr>
						<td width="50%">Срок начала строительства объекта:</td>
						<td>
							<xsl:call-template name="FormatDate">
								<xsl:with-param name="DateTimeStr" select="@BeginDate"/>
							</xsl:call-template>
						</td>
					</tr>
				</xsl:if>
				<xsl:if test="@EndDate">
					<tr>
						<td width="50%">Срок окончания строительства объекта:</td>
						<td>
							<xsl:call-template name="FormatDate">
								<xsl:with-param name="DateTimeStr" select="@EndDate"/>
							</xsl:call-template>
						</td>
					</tr>	
				</xsl:if>
				<xsl:if test="@OperationDate">
					<tr>
						<td width="50%">Срок ввода объекта в эксплуатацию:</td>
						<td>
							<xsl:call-template name="FormatDate">
								<xsl:with-param name="DateTimeStr" select="@OperationDate"/>
							</xsl:call-template>
						</td>
					</tr>
				</xsl:if>
			</table>
		</xsl:if>
		<xsl:if test="$show=5">
			<xsl:choose>
				<xsl:when test="ProjectDocuments/NotIndustrialObject/ProjectDocumentation">
					<xsl:call-template name="NotLinearProjectDocumentsContent">
						<xsl:with-param name="DocumentationContent" select="ProjectDocuments/NotIndustrialObject/ProjectDocumentation"/>
					</xsl:call-template>
				</xsl:when>
				<xsl:when test="ProjectDocuments/IndustrialObject/ProjectDocumentation">
					<xsl:call-template name="NotLinearProjectDocumentsContent">
						<xsl:with-param name="DocumentationContent" select="ProjectDocuments/IndustrialObject/ProjectDocumentation"/>
					</xsl:call-template>
				</xsl:when>
				<xsl:when test="ProjectDocuments/LinearObject/ProjectDocumentation">
					<xsl:call-template name="LinearProjectDocumentsContent">
						<xsl:with-param name="DocumentationContent" select="ProjectDocuments/LinearObject/ProjectDocumentation"/>
					</xsl:call-template>
				</xsl:when>
				<xsl:otherwise>
					<p class="border">Требования отсутствуют</p>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:if test="ProjectDocuments/./Note">
				<p class="upper">Дополнительные требования:</p>
				<xsl:call-template name="TextBlockInTable">
					<xsl:with-param name="obj" select="ProjectDocuments/./Note"/>
				</xsl:call-template>
			</xsl:if>
		</xsl:if>
		<xsl:if test="$show=6">
			<xsl:choose>
				<xsl:when test="$SectionName='Estimate'">
					<xsl:call-template name="TextBlockInTable">
						<xsl:with-param name="obj" select="Estimate"/>
					</xsl:call-template>
					<xsl:if test="not(Estimate)">
						<p class="border">Требования отсутствуют</p>
					</xsl:if>
				</xsl:when>
				<xsl:when test="$SectionName='SpecialTechnicalConditions'">
					<xsl:call-template name="TextBlockInTable">
						<xsl:with-param name="obj" select="SpecialTechnicalConditions"/>
					</xsl:call-template>
					<xsl:if test="not(SpecialTechnicalConditions)">
						<p class="border">Требования отсутствуют</p>
					</xsl:if>
				</xsl:when>
				<xsl:when test="$SectionName='Standardization'">
					<xsl:call-template name="TextBlockInTable">
						<xsl:with-param name="obj" select="Standardization"/>
					</xsl:call-template>
					<xsl:if test="not(Standardization)">
						<p class="border">Требования отсутствуют</p>
					</xsl:if>
				</xsl:when>
				<xsl:when test="$SectionName='Demonstration'">
					<xsl:call-template name="TextBlockInTable">
						<xsl:with-param name="obj" select="Demonstration"/>
					</xsl:call-template>
					<xsl:if test="not(Demonstration)">
						<p class="border">Требования отсутствуют</p>
					</xsl:if>
				</xsl:when>
				<xsl:when test="$SectionName='InformationModel'">
					<xsl:call-template name="TextBlockInTable">
						<xsl:with-param name="obj" select="InformationModel"/>
					</xsl:call-template>
					<xsl:if test="not(InformationModel)">
						<p class="border">Требования отсутствуют</p>
					</xsl:if>
				</xsl:when>
				<xsl:when test="$SectionName='TypicalDesign'">
					<xsl:call-template name="TextBlockInTable">
						<xsl:with-param name="obj" select="TypicalDesign"/>
					</xsl:call-template>
					<xsl:if test="not(TypicalDesign)">
						<p class="border">Требования отсутствуют</p>
					</xsl:if>
				</xsl:when>
				<xsl:when test="$SectionName='OtherRequirements'">
					<xsl:call-template name="TextBlockInTable">
						<xsl:with-param name="obj" select="OtherRequirements"/>
					</xsl:call-template>
					<xsl:if test="not(OtherRequirements)">
						<p class="border">Требования отсутствуют</p>
					</xsl:if>
				</xsl:when>
			</xsl:choose>
		</xsl:if>		
	</xsl:template>
	
	<xsl:template name="AdjacentsObjects">
		<a name="ch18"/>
		<h3 class="bckgr upper">18. Смежные объекты капитального строительства</h3>
		
		<xsl:if test="/Document/Content/Adjacents">
			<xsl:apply-templates select="/Document/Content/Adjacents/AdjacentObject"/>
		</xsl:if>
		<xsl:if test="not(/Document/Content/Adjacents/AdjacentObject)">
			<table><tr><td><p>Cмежные объекты капитального строительства отсутствуют</p></td></tr></table>
		</xsl:if>
	</xsl:template>

	<xsl:template match="AdjacentObject">
		<h4 class="upper under"><xsl:value-of select="Name"/></h4>
		<table>
			<xsl:variable name="OLD" select="TEI/OldValue or TEI/OldMinValue"/>
			
			<xsl:for-each select="Crossing|Following">
				<xsl:if test="name()='Crossing'">
					<tr>
						<td colspan="4">
							<xsl:if test="$OLD">
								<xsl:attribute name="colspan">6</xsl:attribute>
							</xsl:if>
							<p class="upper italic under">Пересечение:</p>
						</td>
					</tr>
					<tr>
						<td width="25%">Адрес пересечения:</td>
						<td colspan="3">
							<xsl:if test="$OLD">
								<xsl:attribute name="colspan">5</xsl:attribute>
							</xsl:if>
							<xsl:apply-templates select="."/>
						</td>
					</tr>
				</xsl:if>
				<xsl:if test="name()='Following'">
					<tr>
						<td colspan="4">
							<xsl:if test="$OLD">
								<xsl:attribute name="colspan">6</xsl:attribute>
							</xsl:if>
							<p class="upper italic under">Параллельное следование:</p>
						</td>
					</tr>
					
					<tr>
						<td>Адрес начального пункта линейного объекта:</td>
						<td colspan="3">
							<xsl:if test="$OLD">
								<xsl:attribute name="colspan">5</xsl:attribute>
							</xsl:if>
							<xsl:apply-templates select="BeginAddress"/>
						</td>
					</tr>
					<tr>
						<td>Адрес конечного пункта линейного объекта:</td>
						<td colspan="3">
							<xsl:if test="$OLD">
								<xsl:attribute name="colspan">5</xsl:attribute>
							</xsl:if>
							<xsl:apply-templates select="FinalAddress"/>
						</td>
					</tr>
					<xsl:for-each select="Length">
						<tr>
							<td>Протяженность параллельного следования (<xsl:apply-templates select="Measure"/>):</td>
							<td colspan="3">
								<xsl:if test="$OLD">
									<xsl:attribute name="colspan">5</xsl:attribute>
								</xsl:if>
								<xsl:value-of select="Value"/>
							</td>
						</tr>
					</xsl:for-each>
				</xsl:if>
			</xsl:for-each>
			<tr>
				<td colspan="4" class="not-border">
					<xsl:if test="$OLD">
						<xsl:attribute name="colspan">6</xsl:attribute>
					</xsl:if>
				</td>
			</tr>
			<xsl:if test="@Code">
				<tr>
					<td>Код объекта капитального строительства:</td>
					<td colspan="3">
						<xsl:if test="$OLD">
							<xsl:attribute name="colspan">5</xsl:attribute>
						</xsl:if>
						<xsl:value-of select="@Code"/></td>
				</tr>
			</xsl:if>
			<xsl:if test="Designers">
				<tr>
					<td>Разработчик документации:</td>
					<td colspan="3">
						<xsl:if test="$OLD">
							<xsl:attribute name="colspan">5</xsl:attribute>
						</xsl:if>
						<xsl:apply-templates select="Designers/*">
							<xsl:with-param name="ShowType">1</xsl:with-param>
						</xsl:apply-templates>
					</td>
				</tr>
			</xsl:if>
			<tr>
				<td>Владелец объекта:</td>
				<td colspan="3">
					<xsl:if test="$OLD">
						<xsl:attribute name="colspan">5</xsl:attribute>
					</xsl:if>
					<xsl:apply-templates select="Owners/*">
						<xsl:with-param name="ShowType">1</xsl:with-param>
					</xsl:apply-templates>
				</td>
			</tr>
			<xsl:if test="Note">
				<tr>
					<td>Дополнительные сведения:</td>
					<td colspan="3">
						<xsl:if test="$OLD">
							<xsl:attribute name="colspan">5</xsl:attribute>
						</xsl:if>
						<xsl:value-of select="Note"/>
					</td>
				</tr>
			</xsl:if>
		</table>

		<xsl:if test="TEI">
			<xsl:call-template name="POITEI">
				<xsl:with-param name="Obj" select="TEI"/>
			</xsl:call-template>
		</xsl:if>
		
	</xsl:template>

	<xsl:template name="ObjectsProjectSolutions">
		
		<xsl:for-each select="/Document/Content/Object/ProjectSolutions">
			<a name="ch20"/>
			<h3 class="bckgr upper">20.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">SchemePlanningOrganizationLand</xsl:with-param>
				</xsl:call-template>
			</h3>	
			<h4 class="upper under">20.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="SchemePlanningOrganizationLand/Requirements"/>
			<xsl:apply-templates select="SchemePlanningOrganizationLand/ComponentRequirements"/>
			<xsl:if test="not(SchemePlanningOrganizationLand)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">20.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">SchemePlanningOrganizationLand</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch21"/>
			<h3 class="bckgr upper">21.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">RightOfWayProject</xsl:with-param>
				</xsl:call-template>
			</h3>	
			<h4 class="upper under">21.1. Объект капитального строительства</h4>
			<xsl:apply-templates select="RightOfWayProject/Requirements"/>
			<xsl:apply-templates select="RightOfWayProject/ComponentRequirements"/>
			<xsl:if test="not(RightOfWayProject)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">21.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">RightOfWayProject</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch22"/>
			<h3 class="bckgr upper">22.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">ArchitectSolutions</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">22.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="ArchitectSolutions/Zones"/>
			<xsl:apply-templates select="ArchitectSolutions/Requirements"/>
			<xsl:apply-templates select="ArchitectSolutions/ComponentRequirements"/>
			<xsl:if test="not(ArchitectSolutions)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">22.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">ArchitectSolutions</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch23"/>
			<h3 class="bckgr upper">23.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">TechnologicalSolutions</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">23.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="TechnologicalSolutions/Requirements"/>
			<xsl:apply-templates select="TechnologicalSolutions/ComponentRequirements"/>
			<xsl:if test="not(TechnologicalSolutions)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">23.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">TechnologicalSolutions</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch24"/>
			<h3 class="bckgr upper">24.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">StructuralSpacePlanningSolutions</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">24.1. Объект капитального строительства:</h4>
			
			<xsl:for-each select="StructuralSpacePlanningSolutions/Section">
				<h4 class="upper under">
					<xsl:call-template name="StructuralSpacePlanningSolutionsSectionsName">
						<xsl:with-param name="Name" select="@Name"/>
					</xsl:call-template>:
				</h4>	
				<xsl:apply-templates select="Requirements"/>
				<xsl:apply-templates select="ComponentRequirements"/>
			</xsl:for-each>
			
			<xsl:if test="not(StructuralSpacePlanningSolutions)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">24.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">StructuralSpacePlanningSolutions</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch25"/>
			<h3 class="bckgr upper">25.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">TechnologicalConstructiveSolutions</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">25.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="TechnologicalConstructiveSolutions/Requirements"/>
			<xsl:apply-templates select="TechnologicalConstructiveSolutions/ComponentRequirements"/>
			<xsl:if test="not(TechnologicalConstructiveSolutions)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">25.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">TechnologicalConstructiveSolutions</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch26"/>
			<h3 class="bckgr upper">26.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">InfrastructureLinearObject</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">26.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="InfrastructureLinearObject/Requirements"/>
			<xsl:apply-templates select="InfrastructureLinearObject/ComponentRequirements"/>
			<xsl:if test="not(InfrastructureLinearObject)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">26.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">InfrastructureLinearObject</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch27"/>
			<h3 class="bckgr upper">27.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">EngineeringTechnicalSolutions</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">27.1. Объект капитального строительства:</h4>
			
			<h4 class="under upper">27.1.1. Требования к основному технологическому оборудованию:</h4>
			<xsl:for-each select="EngineeringTechnicalSolutions/TechnologicalEquipment">
				<h4 class="upper under">
					<xsl:call-template name="EngineeringTechnicalSystemsName">
						<xsl:with-param name="Name" select="@Name"/>
					</xsl:call-template>:
				</h4>	
				<xsl:apply-templates select="Requirements"/>
				<xsl:apply-templates select="ComponentRequirements"/>
			</xsl:for-each>
			<xsl:if test="not(EngineeringTechnicalSolutions/TechnologicalEquipment)"><p class="border">Требования отсутствуют</p></xsl:if>
			
			<h4 class="under upper">27.1.2. Требования к наружным сетям инженерно-технического обеспечения, точкам присоединения:</h4>
			<xsl:for-each select="EngineeringTechnicalSolutions/ExternalEngineeringNetwork">
				<h4 class="upper under">
					<xsl:call-template name="EngineeringTechnicalSystemsNetworkName">
						<xsl:with-param name="Name" select="@Name"/>
					</xsl:call-template>:
				</h4>	
				<xsl:apply-templates select="Requirements"/>
				<xsl:apply-templates select="ComponentRequirements"/>
			</xsl:for-each>
			<xsl:if test="not(EngineeringTechnicalSolutions/ExternalEngineeringNetwork)"><p class="border">Требования отсутствуют</p></xsl:if>
			
			<xsl:apply-templates select="EngineeringTechnicalSolutions/Requirements"/>
			<xsl:apply-templates select="EngineeringTechnicalSolutions/ComponentRequirements"/>
			
			<h4 class="upper under">27.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">EngineeringTechnicalSolutions</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch28"/>
			<h3 class="bckgr upper">28.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">EnvironmentalProtection</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">28.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="EnvironmentalProtection/Requirements"/>
			<xsl:apply-templates select="EnvironmentalProtection/ComponentRequirements"/>
			<xsl:if test="not(EnvironmentalProtection)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">28.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">EnvironmentalProtection</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch29"/>
			<h3 class="bckgr upper">29.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">FireSafetyMeasures</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">29.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="FireSafetyMeasures/Requirements"/>
			<xsl:apply-templates select="FireSafetyMeasures/ComponentRequirements"/>
			<xsl:if test="not(FireSafetyMeasures)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">29.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">FireSafetyMeasures</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch30"/>
			<h3 class="bckgr upper">30.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">EnergyEfficiencyRequirements</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">30.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="EnergyEfficiencyRequirements/Requirements"/>
			<xsl:apply-templates select="EnergyEfficiencyRequirements/ComponentRequirements"/>
			<xsl:if test="not(EnergyEfficiencyRequirements)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">30.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">EnergyEfficiencyRequirements</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch31"/>
			<h3 class="bckgr upper">31.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">LowMobilityGroupsPopulation</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">31.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="LowMobilityGroupsPopulation/Requirements"/>
			<xsl:apply-templates select="LowMobilityGroupsPopulation/ComponentRequirements"/>
			<xsl:if test="not(LowMobilityGroupsPopulation)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">31.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">LowMobilityGroupsPopulation</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch32"/>
			<h3 class="bckgr upper">32.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">EngineeringTechnicalStrengthening</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">32.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="EngineeringTechnicalStrengthening/Requirements"/>
			<xsl:apply-templates select="EngineeringTechnicalStrengthening/ComponentRequirements"/>
			<xsl:if test="not(EngineeringTechnicalStrengthening)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">32.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">EngineeringTechnicalStrengthening</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch33"/>
			<h3 class="bckgr upper">33.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">SafeLivingConditions</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">33.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="SafeLivingConditions/Requirements"/>
			<xsl:apply-templates select="SafeLivingConditions/ComponentRequirements"/>
			<xsl:if test="not(SafeLivingConditions)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">33.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">SafeLivingConditions</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch34"/>
			<h3 class="bckgr upper">34.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">TechnicalOperation</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">34.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="TechnicalOperation/Requirements"/>
			<xsl:apply-templates select="TechnicalOperation/ComponentRequirements"/>
			<xsl:if test="not(TechnicalOperation)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">34.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">TechnicalOperation</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch35"/>
			<h3 class="bckgr upper">35.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">ConstructionOrganizationProject</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">35.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="ConstructionOrganizationProject/Requirements"/>
			<xsl:apply-templates select="ConstructionOrganizationProject/ComponentRequirements"/>
			<xsl:if test="not(ConstructionOrganizationProject)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">35.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">ConstructionOrganizationProject</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch36"/>
			<h3 class="bckgr upper">36.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">DemolishPreserveBuildings</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">36.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="DemolishPreserveBuildings/Requirements"/>
			<xsl:apply-templates select="DemolishPreserveBuildings/ComponentRequirements"/>
			<xsl:if test="not(DemolishPreserveBuildings)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">36.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">DemolishPreserveBuildings</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch37"/>
			<h3 class="bckgr upper">37.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">Landscaping</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">37.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="Landscaping/Requirements"/>
			<xsl:apply-templates select="Landscaping/ComponentRequirements"/>
			<xsl:if test="not(Landscaping)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">37.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">Landscaping</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch38"/>
			<h3 class="bckgr upper">38.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">LandReclamationProject</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">38.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="LandReclamationProject/Requirements"/>
			<xsl:apply-templates select="LandReclamationProject/ComponentRequirements"/>
			<xsl:if test="not(LandReclamationProject)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">38.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">LandReclamationProject</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch39"/>
			<h3 class="bckgr upper">39.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">StorageLocations</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">39.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="StorageLocations/Requirements"/>
			<xsl:apply-templates select="StorageLocations/ComponentRequirements"/>
			<xsl:if test="not(StorageLocations)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">39.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">StorageLocations</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
			<!-- -->
			<a name="ch40"/>
			<h3 class="bckgr upper">40.
				<xsl:call-template name="ProjectSolutionsName">
					<xsl:with-param name="Name">ResearchDevelopmentWork</xsl:with-param>
				</xsl:call-template>
			</h3>
			<h4 class="upper under">40.1. Объект капитального строительства:</h4>
			<xsl:apply-templates select="ResearchDevelopmentWork/Requirements"/>
			<xsl:apply-templates select="ResearchDevelopmentWork/ComponentRequirements"/>
			<xsl:if test="not(ResearchDevelopmentWork)">
				<p class="border black">Требования отсутствуют</p>	
			</xsl:if>
			<h4 class="upper under">40.2. Объекты капитального строительства, входящие в состав:</h4>
			<table><tr><td>
				<xsl:apply-templates select="../ObjectParts">
					<xsl:with-param name="level" select="1."/>
					<xsl:with-param name="show" select="2"/>
					<xsl:with-param name="SectionName">ResearchDevelopmentWork</xsl:with-param>
				</xsl:apply-templates>
				<xsl:if test="not(../ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
			</td></tr></table>
		</xsl:for-each>
	</xsl:template>
	
	<xsl:template match="Zones">
		<table class="margin-bottom-small">
			<thead>
				<tr><th colspan="8">Требования к зонированию и помещениям</th></tr>
				<tr><th width="5%" rowspan="2">№ п/п</th><th colspan="2">Зона</th><th colspan="4">Помещение</th></tr>
				<tr><th>Наименование</th><th>Количество</th><th>Наименование</th><th>Количество</th><th width="10%">Минимальная площадь</th></tr>
			</thead>
			<tbody>
				<xsl:variable name="PremiseNumber" select="count(Zone) + count(Zone/Premise)"/>
				<xsl:for-each select="Zone">
					<tr>
						<td>
							<xsl:attribute name="rowspan">
								<xsl:value-of select="count(Premise)+1"/>
							</xsl:attribute>
							<xsl:value-of select="position()"/>.
						</td>
						<td>
							<xsl:attribute name="rowspan">
								<xsl:value-of select="count(Premise)+1"/>
							</xsl:attribute>
							<xsl:value-of select="@Name"/> 
						</td>
						<td class="center">
							<xsl:attribute name="rowspan">
								<xsl:value-of select="count(Premise)+1"/>
							</xsl:attribute>
							<xsl:value-of select="@Count"/>
							<xsl:if test="not(@Count)">-</xsl:if>
						</td>
						<xsl:if test="not(Premise)">
							<td class="center">-</td>
							<td class="center">-</td>
							<td class="center">-</td>
						</xsl:if>
					</tr>
					<xsl:for-each select="Premise">
						<tr>
							<td>
								<xsl:value-of select="@Name"/>
							</td>
							<td class="center">
								<xsl:value-of select="@Count"/>
								<xsl:if test="not(@Count)">-</xsl:if>
							</td>
							<td class="center">
								<xsl:value-of select="@MinArea"/><xsl:text> </xsl:text><xsl:apply-templates select="@Measure"/>
								<xsl:if test="not(@MinArea)">-</xsl:if>
							</td>
						</tr>
					</xsl:for-each>
				</xsl:for-each>
			</tbody>
		</table>		
	</xsl:template>

	<xsl:template match="Requirements">
		
		<table class="margin-bottom-small">
			<thead>
				<tr><th width="5%">№ п/п</th><th>Требование</th></tr>
			</thead>
			<tbody>
				<xsl:for-each select="Requirement">
					
					<xsl:if test="Norms|Author">
						<tr>
							<td>
								<xsl:attribute name="rowspan">
									<xsl:value-of select="count(Content|Norms|Author)"/>
								</xsl:attribute>
								<xsl:value-of select="position()"/>.
							</td>
							<td>
								<xsl:if test="Content/@Title">
									<h5><xsl:value-of select="Content/@Title"/></h5>
								</xsl:if>
								<xsl:apply-templates select="Content/."/>
							</td>
						</tr>
						<xsl:if test="Norms">
							<tr>
								<td>
									<p class="upper">Перечень ссылок на требования нормативных документов:</p>
									<xsl:for-each select="Norms/Norm">
										<p>- <xsl:value-of select="."/>;</p>
									</xsl:for-each>	
								</td>
							</tr>
						</xsl:if>
						<xsl:if test="Author">
							<tr>
								<td><p class="upper">Автор:</p><p><xsl:value-of select="Author"/></p></td>
							</tr>
						</xsl:if>
					</xsl:if>
					<xsl:if test="not(Norms|Author)">
						<tr><td><xsl:value-of select="position()"/>.</td>
							<td>
								<xsl:if test="Content/@Title">
									<h5><xsl:value-of select="Content/@Title"/></h5>
								</xsl:if>
								<xsl:apply-templates select="Content/."/>
							</td>
						</tr>
					</xsl:if>
				</xsl:for-each>
			</tbody>
		</table>
	</xsl:template>
		
	<xsl:template match="ComponentRequirements">
		<p class="under upper pad-left"><xsl:value-of select="Name"/></p>
		<xsl:if test="Description">
			<p class="italic pad-left"><xsl:value-of select="Description"/></p>
		</xsl:if>
		<xsl:apply-templates select="Requirements"/>
	</xsl:template>

	<xsl:template name="ObjectsProjectDocuments">
		<a name="ch41"/>
		<h3 class="bckgr upper">41. Требования к составу проектной документации, в том числе требования о разработке разделов проектной документации, наличие которых не является обязательным</h3>
		<h4 class="upper under">41.1. Объект капитального строительства:</h4>
		
		<xsl:choose>
			<xsl:when test="/Document/Content/Object/ProjectDocuments/NotIndustrialObject">
				<xsl:call-template name="NotLinearProjectDocumentsContent">
					<xsl:with-param name="DocumentationContent" select="/Document/Content/Object/ProjectDocuments/NotIndustrialObject/ProjectDocumentation"/>
				</xsl:call-template>
			</xsl:when>
			<xsl:when test="/Document/Content/Object/ProjectDocuments/IndustrialObject">
				<xsl:call-template name="NotLinearProjectDocumentsContent">
					<xsl:with-param name="DocumentationContent" select="/Document/Content/Object/ProjectDocuments/IndustrialObject/ProjectDocumentation"/>
				</xsl:call-template>
			</xsl:when>
			<xsl:when test="/Document/Content/Object/ProjectDocuments/LinearObject">
				<xsl:call-template name="LinearProjectDocumentsContent">
					<xsl:with-param name="DocumentationContent" select="/Document/Content/Object/ProjectDocuments/LinearObject/ProjectDocumentation"/>
				</xsl:call-template>
			</xsl:when>
		</xsl:choose>
		
		<xsl:if test="count(/Document/Content/Object/ProjectDocuments/*/ProjectDocumentation/*)=0">
			<table><tr><td>Требования к составу и содержанию разделов проектной документации отсутствуют</td></tr></table>
		</xsl:if>

		<xsl:if test="/Document/Content/Object/ProjectDocuments/Note">
			<p class="upper bold under">Дополнительные требования:</p>
			<xsl:call-template name="TextBlockInTable">
				<xsl:with-param name="obj" select="/Document/Content/Object/ProjectDocuments/Note"/>
			</xsl:call-template>
		</xsl:if>

		<h4 class="upper under">41.2. Объекты капитального строительства, входящие в состав:</h4>
		<table><tr><td>
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="5"/>
			</xsl:apply-templates>
			<xsl:if test="not(/Document/Content/Object/ObjectParts)"><p>Требования отсутствуют</p></xsl:if>
		</td></tr></table>
	</xsl:template>
		
	<xsl:template name="LinearProjectDocumentsContent">
		<xsl:param name="DocumentationContent"/>
		<xsl:if test="$DocumentationContent/*">
			<table>
				<thead>
					<tr><th width="5%">№ <nobr>п/п</nobr></th><th>Требование к разделу (подразделу)</th></tr>
				</thead>
				<tbody>
					<xsl:for-each select="$DocumentationContent/*">
						<tr>
							<td class="bold" colspan="2">
								<xsl:call-template name="LinearProjectDocumentsSectionName">
									<xsl:with-param name="SectionNumber" select="name()"/>
								</xsl:call-template>
							</td>
						</tr>
						<xsl:choose>
							<xsl:when test="name() = 'Section9' or name() = 'Section10'">
								<xsl:for-each select="./*">
									<tr>
										<tr>
											<td class="bold" colspan="2">
												<xsl:call-template name="NotLinearProjectDocumentsSectionName">
													<xsl:with-param name="SectionNumber" select="name()"/>
												</xsl:call-template>
											</td>
										</tr>
									</tr>
									<xsl:call-template name="SectionDocRequirements">
										<xsl:with-param name="obj" select="SectionRequirement"/>	
									</xsl:call-template>
									<xsl:for-each select="./SubSection">
										<xsl:call-template name="SetSubSection">
											<xsl:with-param name="SubSection" select="."/>
										</xsl:call-template>
									</xsl:for-each>
									<xsl:if test="not(SectionRequirement) and not(./SubSection)">
										<tr><td colspan="2"><p>Требования отсутствуют</p></td></tr>
									</xsl:if>
								</xsl:for-each>
							</xsl:when>
							<xsl:otherwise>
								<xsl:call-template name="SectionDocRequirements">
									<xsl:with-param name="obj" select="SectionRequirement"/>	
								</xsl:call-template>
								<xsl:for-each select="./SubSection">
									<xsl:call-template name="SetSubSection">
										<xsl:with-param name="SubSection" select="."/>
									</xsl:call-template>
								</xsl:for-each>
								<xsl:if test="not(SectionRequirement) and not(./SubSection)">
									<tr><td><p>Требования отсутствуют</p></td></tr>
								</xsl:if>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:for-each>
				</tbody>
			</table>
		</xsl:if>
	</xsl:template>
		
	<xsl:template name="NotLinearProjectDocumentsContent">
		<xsl:param name="DocumentationContent"/>
		<xsl:if test="$DocumentationContent/*">
			<table>
				<thead>
					<tr><th width="5%">№ <nobr>п/п</nobr></th><th>Требование к разделу (подразделу)</th></tr>
				</thead>
				<tbody>
					<xsl:for-each select="$DocumentationContent/*">
						<tr>
							<td class="bold" colspan="2">
								<xsl:call-template name="NotLinearProjectDocumentsSectionName">
									<xsl:with-param name="SectionNumber" select="name()"/>
								</xsl:call-template>
							</td>
						</tr>
						<xsl:choose>
							<xsl:when test="(name()='Section5') or (name()='Section12') or (name()='Section13')">
								<xsl:for-each select="./*">
									<tr>
										<tr>
											<td class="bold" colspan="2">
												<xsl:call-template name="NotLinearProjectDocumentsSectionName">
													<xsl:with-param name="SectionNumber" select="name()"/>
												</xsl:call-template>
											</td>
										</tr>
									</tr>
									<xsl:call-template name="SectionDocRequirements">
										<xsl:with-param name="obj" select="SectionRequirement"/>	
									</xsl:call-template>
									<xsl:for-each select="./SubSection">
										<xsl:call-template name="SetSubSection">
											<xsl:with-param name="SubSection" select="."/>
										</xsl:call-template>
									</xsl:for-each>
									<xsl:if test="not(SectionRequirement) and not(./SubSection)">
										<tr><td colspan="2"><p>Требования отсутствуют</p></td></tr>
									</xsl:if>
								</xsl:for-each>
								
							</xsl:when>
							<xsl:otherwise>
								<xsl:call-template name="SectionDocRequirements">
									<xsl:with-param name="obj" select="SectionRequirement"/>	
								</xsl:call-template>
								<xsl:for-each select="./SubSection">
									<xsl:call-template name="SetSubSection">
										<xsl:with-param name="SubSection" select="."/>
									</xsl:call-template>
								</xsl:for-each>
								<xsl:if test="not(SectionRequirement) and not(./SubSection)">
									<tr><td colspan="2"><p>Требования отсутствуют</p></td></tr>
								</xsl:if>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:for-each>
				</tbody>
			</table>
		</xsl:if>
	</xsl:template>

	<xsl:template name="SectionDocRequirements">
		<xsl:param name="obj"/>
		<xsl:for-each select="$obj">
			<xsl:if test="Norms">
				<tr>
					<td>
						<xsl:attribute name="rowspan">2</xsl:attribute>
						<xsl:value-of select="position()"/>.
					</td>
					<td>
						<xsl:if test="Requirement/@Title">
							<h5><xsl:value-of select="Requirement/@Title"/></h5>
						</xsl:if>
						<xsl:apply-templates select="Requirement/*"/>
					</td>
				</tr>
				<tr>
					<td>
						<p class="upper">Перечень ссылок на требования нормативных документов:</p>
						<xsl:for-each select="Norms/Norm">
							<p>- <xsl:value-of select="."/>;</p>
						</xsl:for-each>	
					</td>
				</tr>
			</xsl:if>
			<xsl:if test="not(Norms)">
				<tr><td><xsl:value-of select="position()"/>.</td>
					<td>
						<xsl:if test="Requirement/@Title">
							<h5><xsl:value-of select="Requirement/@Title"/></h5>
						</xsl:if>
						<xsl:apply-templates select="Requirement/*"/>
					</td>
				</tr>
			</xsl:if>
		</xsl:for-each>
	</xsl:template>
		
	<xsl:template name="SetSubSection">
		<xsl:param name="SubSection"/>
		<tr>
			<td class="bold italic" colspan="2">
				<xsl:value-of select="$SubSection/@Name"/>:
			</td>
		</tr>
		<xsl:call-template name="SectionDocRequirements">
			<xsl:with-param name="obj" select="SectionRequirement"/>	
		</xsl:call-template>
		<xsl:for-each select="./SubSection">
			<xsl:call-template name="SetSubSection">
				<xsl:with-param name="SubSection" select="."/>
			</xsl:call-template>
		</xsl:for-each>
		<xsl:if test="not(SectionRequirement) and not(./SubSection)">
			<tr><td colspan="2"><p>Требования отсутствуют</p></td></tr>
		</xsl:if>
	</xsl:template>

	<xsl:template name="ProjectSolutionsName">
		<xsl:param name="Name"/>
		<xsl:choose>
			<xsl:when test="$Name = 'SchemePlanningOrganizationLand'">Требования к схеме планировочной организации земельного участка</xsl:when>
			<xsl:when test="$Name = 'RightOfWayProject'">Требования к проекту полосы отвода</xsl:when>
			<xsl:when test="$Name = 'ArchitectSolutions'">Требования к архитектурно-художественным решениям, включая требования к графическим материалам</xsl:when>
			<xsl:when test="$Name = 'TechnologicalSolutions'">Требования к технологическим решениям</xsl:when>
			<xsl:when test="$Name = 'StructuralSpacePlanningSolutions'">Требования к конструктивным и объемно-планировочным решениям</xsl:when>
			<xsl:when test="$Name = 'TechnologicalConstructiveSolutions'">Требования к технологическим и конструктивным решениям линейного объекта</xsl:when>
			<xsl:when test="$Name = 'InfrastructureLinearObject'">Требования к зданиям, строениям и сооружениям, входящим в инфраструктуру линейного объекта</xsl:when>
			<xsl:when test="$Name = 'EngineeringTechnicalSolutions'">Требования к инженерно-техническим решениям</xsl:when>
			<xsl:when test="$Name = 'EnvironmentalProtection'">Требования к мероприятиям по охране окружающей среды</xsl:when>
			<xsl:when test="$Name = 'FireSafetyMeasures'">Требования к мероприятиям по обеспечению пожарной безопасности</xsl:when>
			<xsl:when test="$Name = 'EnergyEfficiencyRequirements'">Требования к мероприятиям по обеспечению соблюдения требований энергетической эффективности и по оснащенности объекта приборами учета используемых энергетических ресурсов</xsl:when>
			<xsl:when test="$Name = 'LowMobilityGroupsPopulation'">Требования к мероприятиям по обеспечению доступа маломобильных групп населения к объекту</xsl:when>
			<xsl:when test="$Name = 'EngineeringTechnicalStrengthening'">Требования к инженерно-техническому укреплению объекта в целях обеспечения его антитеррористической защищенности</xsl:when>
			<xsl:when test="$Name = 'SafeLivingConditions'">Требования к соблюдению безопасных для здоровья человека условий проживания и пребывания в объекте и требования к соблюдению безопасного уровня воздействия объекта на окружающую среду</xsl:when>
			<xsl:when test="$Name = 'TechnicalOperation'">Требования к технической эксплуатации и техническому обслуживанию объекта</xsl:when>
			<xsl:when test="$Name = 'ConstructionOrganizationProject'">Требования к проекту организации строительства объекта</xsl:when>
			<xsl:when test="$Name = 'DemolishPreserveBuildings'">Требования о необходимости сноса или сохранения зданий, сооружений, вырубки или сохранения зеленых насаждений, реконструкции, капитального ремонта существующих линейных объектов в связи с планируемым строительством объекта, расположенных на земельном участке, на котором планируется строительство объекта</xsl:when>
			<xsl:when test="$Name = 'Landscaping'">Требования к решениям по благоустройству прилегающей территории, малым архитектурным формам и планировочной организации земельного участка</xsl:when>
			<xsl:when test="$Name = 'LandReclamationProject'">Требования к разработке проекта рекультивации земель</xsl:when>
			<xsl:when test="$Name = 'StorageLocations'">Требования к местам складирования излишков грунта и (или) мусора при строительстве и протяженность маршрута их доставки</xsl:when>
			<xsl:when test="$Name = 'ResearchDevelopmentWork'">Требования к выполнению научно-исследовательских и опытно-конструкторских работ в процессе проектирования и строительства объекта</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template name="StructuralSpacePlanningSolutionsSectionsName">
		<xsl:param name="Name"/>
		<xsl:choose>
			<xsl:when test="$Name = 'OrderSelection'">Порядок выбора и применения материалов, изделий, конструкций, оборудования и их согласования застройщиком (техническим заказчиком)</xsl:when>
			<xsl:when test="$Name = 'BuildingStructures'">Требования к строительным конструкциям</xsl:when>
			<xsl:when test="$Name = 'Foundations'">Требования к фундаментам</xsl:when>
			<xsl:when test="$Name = 'WallsBasementsGroundFloor'">Требования к стенам, подвалам и цокольному этажу</xsl:when>
			<xsl:when test="$Name = 'ExternalWalls'">Требования к наружным стенам</xsl:when>
			<xsl:when test="$Name = 'InternalWalls'">Требования к внутренним стенам и перегородкам</xsl:when>
			<xsl:when test="$Name = 'Overlaps'">Требования к перекрытиям</xsl:when>
			<xsl:when test="$Name = 'ColumnsCrossbars'">Требования к колоннам, ригелям</xsl:when>
			<xsl:when test="$Name = 'Stairs'">Требования к лестницам</xsl:when>
			<xsl:when test="$Name = 'Floors'">Требования к полам</xsl:when>
			<xsl:when test="$Name = 'Roof'">Требования к кровле</xsl:when>
			<xsl:when test="$Name = 'Windows'">Требования к витражам, окнам</xsl:when>
			<xsl:when test="$Name = 'Doors'">Требования к дверям</xsl:when>
			<xsl:when test="$Name = 'InteriorDecoration'">Требования к внутренней отделке</xsl:when>
			<xsl:when test="$Name = 'ExteriorDecoration'">Требования к наружной отделке</xsl:when>
			<xsl:when test="$Name = 'Security'">Требования к обеспечению безопасности объекта при опасных природных процессах, явлениях и техногенных воздействиях</xsl:when>
			<xsl:when test="$Name = 'EngineeringProtection'">Требования к инженерной защите территории объекта</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template name="EngineeringTechnicalSystemsName">
		<xsl:param name="Name"/>
		<xsl:choose>
			<xsl:when test="$Name = 'Heating'">Отопление</xsl:when>
			<xsl:when test="$Name = 'Ventilation'">Вентиляция</xsl:when>
			<xsl:when test="$Name = 'WaterSupply'">Водопровод</xsl:when>
			<xsl:when test="$Name = 'SewageSystem'">Канализация</xsl:when>
			<xsl:when test="$Name = 'PowerSupply'">Электроснабжение</xsl:when>
			<xsl:when test="$Name = 'Telephony'">Телефонизация</xsl:when>
			<xsl:when test="$Name = 'Radio'">Радиофикация</xsl:when>
			<xsl:when test="$Name = 'Internet'">Информационно-телекоммуникационная сеть "Интернет"</xsl:when>
			<xsl:when test="$Name = 'Television'">Телевидение</xsl:when>
			<xsl:when test="$Name = 'Gasification'">Газификация</xsl:when>
			<xsl:when test="$Name = 'Automation'">Автоматизация и диспетчеризация</xsl:when>
			<xsl:when test="$Name = 'Other'">Иные системы инженерно-технического обеспечения</xsl:when>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="EngineeringTechnicalSystemsNetworkName">
		<xsl:param name="Name"/>
		<xsl:choose>
			<xsl:when test="$Name = 'WaterSupply'">Водоснабжение</xsl:when>
			<xsl:when test="$Name = 'WaterDisposal'">Водоотведение</xsl:when>
			<xsl:when test="$Name = 'HeatSupply'">Теплоснабжение</xsl:when>
			<xsl:when test="$Name = 'PowerSupply'">Электроснабжение</xsl:when>
			<xsl:when test="$Name = 'Telephony'">Телефонизация</xsl:when>
			<xsl:when test="$Name = 'Radio'">Радиофикация</xsl:when>
			<xsl:when test="$Name = 'Internet'">Информационно-телекоммуникационная сеть "Интернет"</xsl:when>
			<xsl:when test="$Name = 'Television'">Телевидение</xsl:when>
			<xsl:when test="$Name = 'GasSupply'">Газоснабжение</xsl:when>
			<xsl:when test="$Name = 'Other'">Иные сети инженерно-технического обеспечения</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template name="LinearProjectDocumentsSectionName">
		<xsl:param name="SectionNumber"/>
		<xsl:choose>
			<xsl:when test="$SectionNumber = 'Section1'">Раздел 1. «Пояснительная записка»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section2'">Раздел 2. «Проект полосы отвода»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section3'">Раздел 3. «Технологические и конструктивные решения линейного объекта. Искусственные сооружения»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section4'">Раздел 4. «Здания, строения и сооружения, входящие в инфраструктуру линейного объекта»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section5'">Раздел 5. «Проект организации строительства»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section6'">Раздел 6. «Мероприятия по охране окружающей среды»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section7'">Раздел 7. «Мероприятия по обеспечению пожарной безопасности»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section8'">Раздел 8. «Требования к обеспечению безопасной эксплуатации линейного объекта»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section9'">Раздел 9. «Смета на строительство, реконструкцию, капитальный ремонт, снос объекта капитального строительства»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section10'">Раздел 10. «Иная документация в случаях, предусмотренных законодательными и иными нормативными правовыми актами Российской Федерации»</xsl:when>
			<xsl:when test="$SectionNumber = 'EstimateExplanatoryNote'">Пояснительная записка к сметной документации</xsl:when>
			<xsl:when test="$SectionNumber = 'CostSummary'">Сводка затрат</xsl:when>
			<xsl:when test="$SectionNumber = 'SummaryEstimate'">Сводный сметный расчет</xsl:when>
			<xsl:when test="$SectionNumber = 'ObjectLocalEstimates'">Объектные и локальные расчеты</xsl:when>
			<xsl:when test="$SectionNumber = 'CostsEstimates'">Сметные расчеты на отдельные виды затрат</xsl:when>
			<xsl:when test="$SectionNumber = 'IndustrialSafetyDeclaration'">Декларация промышленной безопасности опасных производственных объектов</xsl:when>
			<xsl:when test="$SectionNumber = 'HydraulicStructuresSafetyDeclaration'">Декларация безопасности гидротехнических сооружений</xsl:when>
			<xsl:when test="$SectionNumber = 'EventsList'">Перечень мероприятий по гражданской обороне, мероприятий по предупреждению чрезвычайных ситуаций природного и техногенного характера, мероприятий по противодействию терроризму для объектов использования атомной энергии (в том числе ядерных установок, пунктов хранения ядерных материалов и радиоактивных веществ), опасных производственных объектов, определяемых таковыми в соответствии с законодательством Российской Федерации, особо опасных, технически сложных, уникальных объектов, объектов обороны и безопасности</xsl:when>
			<xsl:when test="$SectionNumber = 'OtherDocuments'">Иная документация, установленная законодательными и иными нормативными правовыми актами Российской Федерации</xsl:when>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="NotLinearProjectDocumentsSectionName">
		<xsl:param name="SectionNumber"/>
		<xsl:choose>
			<xsl:when test="$SectionNumber = 'Section1'">Раздел 1. «Пояснительная записка»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section2'">Раздел 2. «Схема планировочной организации земельного участка»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section3'">Раздел 3. «Объемно-планировочные и архитектурные решения»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section4'">Раздел 4. «Конструктивные решения»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section5'">Раздел 5. «Сведения об инженерном оборудовании, о сетях и системах инженерно-технического обеспечения»</xsl:when>
			<xsl:when test="$SectionNumber = 'ElectricitySupply'">Раздел 5. Подраздел «Система электроснабжения»</xsl:when>
			<xsl:when test="$SectionNumber = 'WaterSupply'">Раздел 5. Подраздел «Система водоснабжения»</xsl:when>
			<xsl:when test="$SectionNumber = 'WaterRemoval'">Раздел 5. Подраздел «Система водоотведения»</xsl:when>
			<xsl:when test="$SectionNumber = 'HeatingVentilation'">Раздел 5. Подраздел «Отопление, вентиляция и кондиционирование воздуха, тепловые сети»</xsl:when>
			<xsl:when test="$SectionNumber = 'Communication'">Раздел 5. Подраздел «Сети связи»</xsl:when>
			<xsl:when test="$SectionNumber = 'GasSupply'">Раздел 5. Подраздел «Система газоснабжения»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section6'">Раздел 6. «Технологические решения»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section7'">Раздел 7. «Проект организации строительства»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section8'">Раздел 8. «Мероприятия по охране окружающей среды»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section9'">Раздел 9. «Мероприятия по обеспечению пожарной безопасности»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section10'">Раздел 10. «Требования к обеспечению безопасной эксплуатации объектов капитального строительства»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section11'">Раздел 11. «Мероприятия по обеспечению доступа инвалидов к объекту капитального строительства»</xsl:when>
			<xsl:when test="$SectionNumber = 'Section12'">Раздел 12. «Смета на строительство, реконструкцию, капитальный ремонт, снос объекта капитального строительства»</xsl:when>
			<xsl:when test="$SectionNumber = 'EstimateExplanatoryNote'">Пояснительная записка к сметной документации</xsl:when>
			<xsl:when test="$SectionNumber = 'CostSummary'">Сводка затрат</xsl:when>
			<xsl:when test="$SectionNumber = 'SummaryEstimate'">Сводный сметный расчет</xsl:when>
			<xsl:when test="$SectionNumber = 'ObjectLocalEstimates'">Объектные и локальные расчеты</xsl:when>
			<xsl:when test="$SectionNumber = 'CostsEstimates'">Сметные расчеты на отдельные виды затрат</xsl:when>
			<xsl:when test="$SectionNumber = 'Section13'">Раздел 13. «Иная документация в случаях, предусмотренных законодательными и иными нормативными правовыми актами Российской Федерации»</xsl:when>
			<xsl:when test="$SectionNumber = 'IndustrialSafetyDeclaration'">Декларация промышленной безопасности опасных производственных объектов</xsl:when>
			<xsl:when test="$SectionNumber = 'HydraulicStructuresSafetyDeclaration'">Декларация безопасности гидротехнических сооружений</xsl:when>
			<xsl:when test="$SectionNumber = 'EventsList'">Перечень мероприятий по гражданской обороне, мероприятий по предупреждению чрезвычайных ситуаций природного и техногенного характера, мероприятий по противодействию терроризму для объектов использования атомной энергии (в том числе ядерных установок, пунктов хранения ядерных материалов и радиоактивных веществ), опасных производственных объектов, определяемых таковыми в соответствии с законодательством Российской Федерации, особо опасных, технически сложных, уникальных объектов, объектов обороны и безопасности</xsl:when>
			<xsl:when test="$SectionNumber = 'OtherDocuments'">Иная документация, установленная законодательными и иными нормативными правовыми актами Российской Федерации</xsl:when>
		</xsl:choose>
	</xsl:template>
		
	<xsl:template match="EngineeringSurvey">
		<a name="ch15"/>
		<h3 class="bckgr upper">15. Необходимость выполнения инженерных изысканий для подготовки проектной документации</h3>
		
		<h4 class="upper under">15.1. Общие требования:</h4>
		<xsl:call-template name="TextBlockInTable">
			<xsl:with-param name="obj" select="Common"/>
		</xsl:call-template>	
			
		<xsl:if test="not(SurveyDocuments)">
			<xsl:for-each select="Address">
				<table>
					<tr>
						<td width="25%">Местоположение района (площадки, трассы) проведения инженерных изысканий:</td>
						<td>
							<xsl:apply-templates select="RegionCode"/>
							<xsl:if test="RegionCode!='00'"><xsl:text>, </xsl:text></xsl:if>
							<xsl:if test="RegionCode='00'"><xsl:text>: </xsl:text></xsl:if>
							<xsl:value-of select="District"/>
						</td>
					</tr>
					<xsl:if test="CoordinateSystem">
						<tr>
							<td>Система координат:</td>
							<td>
								<xsl:for-each select="CoordinateSystem">
									<p><xsl:value-of select="."/></p>
								</xsl:for-each>
							</td>
						</tr>
					</xsl:if>
					<xsl:if test="HeightSystem">
						<tr>
							<td>Система высот:</td>
							<td>
								<xsl:for-each select="HeightSystem">
									<p><xsl:value-of select="."/></p>
								</xsl:for-each>
							</td>
						</tr>
					</xsl:if>
				</table>
			</xsl:for-each>	
			
			<xsl:apply-templates select="SurveysRequirements"/>
			
			<xsl:call-template name="SurveyDocumentsRequirements"/>
			
			<xsl:if test="Norms">
				<h4 class="upper under">15.4. Перечень нормативных требований:</h4>
				<table>
					<thead>
						<tr class="bold center"><th width="5%">№ п/п</th><th>Требование</th></tr>
					</thead>
					<tbody>
						<xsl:for-each select="Norms/Norm">
							<tr>
								<td><xsl:number value="position()" format="1. "/></td>
								<td><xsl:value-of select="."/></td>
							</tr>
						</xsl:for-each>
					</tbody>
				</table>
			</xsl:if>
			<h4 class="upper under">
				<xsl:if test="Norms">
					15.5.	
				</xsl:if>
				<xsl:if test="not(Norms)">
					15.4.
				</xsl:if>
				Необходимость использования материалов изысканий прошлых лет:
			</h4>
			<xsl:if test="ReuseDocuments">
				<xsl:apply-templates select="ReuseDocuments"/>	
			</xsl:if>
			<xsl:if test="not(ReuseDocuments)">
				<table><tr><td>Необходимость использования материалов изысканий прошлых лет отсутствует</td></tr></table>
			</xsl:if>	
		</xsl:if>	
		
		<xsl:if test="SurveyDocuments">
			<xsl:apply-templates select="SurveyDocuments"/>
		</xsl:if>
	</xsl:template>
	
	<xsl:template match="SurveysRequirements">
		<h4 class="upper under">15.2. Требования к инженерным изысканиям по виду изысканий:</h4>
		<table>
			<xsl:for-each select="Survey">
				<xsl:if test="position()!=1">
					<tr><td colspan="2" class="not-border"><br/></td></tr>
				</xsl:if>
				<tr class="upper bold">
					<td colspan="2" class="not-border">
						<xsl:if test="@Type">
							<xsl:call-template name="SurveyTypeList">
								<xsl:with-param name="Code" select="@Type"/>
							</xsl:call-template>
						</xsl:if>
						<xsl:if test="@SpecialType">
							<xsl:call-template name="SurveySpecialTypeList">
								<xsl:with-param name="Code" select="@SpecialType"/>
							</xsl:call-template>
						</xsl:if>:
					</td>
				</tr>
				<xsl:if test="Scale">
					<tr>
						<td width="25%">Масштаб:</td>
						<td><xsl:value-of select="Scale"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="MinScale">
					<tr>
						<td width="25%">Минимальный масштаб:</td>
						<td><xsl:value-of select="MinScale"/></td>
					</tr>
					<tr>
						<td>Максимальный масштаб:</td>
						<td><xsl:value-of select="MaxScale"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="Bounds">
					<tr>
						<td>Границы изысканий:</td>
						<td><xsl:value-of select="Bounds"/></td>
					</tr>
				</xsl:if>
				<xsl:if test="Requirements">
					<tr>
						<td colspan="2">
							<xsl:for-each select="Requirements">
								<xsl:if test="@Title">
									<h5><xsl:value-of select="@Title"/></h5>
								</xsl:if>
								<xsl:apply-templates select="./*"/>
							</xsl:for-each>
						</td>
					</tr>
				</xsl:if>
				<xsl:if test="not(Requirements)">
					<tr>
						<td>
							Требования:
						</td>
						<td>
							Отсутствуют
						</td>
					</tr>
				</xsl:if>
			</xsl:for-each>
		</table>
	</xsl:template>
		
	<xsl:template name="SurveyDocumentsRequirements">
		<h4 class="upper under">15.3. Требования к содержанию выпускаемых отчетов и иных технических заданий:</h4>
		<table>
			<xsl:for-each select="/Document/Content/EngineeringSurvey/DocumentsRequirements/Document">
				<xsl:if test="position()!=1">
					<tr><td colspan="2" class="not-border"><br/></td></tr>
				</xsl:if>
				<xsl:call-template name="EngineeringSurveyDocumentTable">
					<xsl:with-param name="Obj" select="."/>
				</xsl:call-template>
			</xsl:for-each>
		</table>
	</xsl:template>
		
	<xsl:template match="ReuseDocuments|SurveyDocuments">
		<table>
			<thead>
				<tr>
					<th width="5%">№ п/п</th>
					<th width="65%">Наименование и реквизиты документа</th>
					<th width="25%">Наименование<br/>файла документа<br/>(подписи к файлу)</th>
					<th>Контрольная сумма файла</th>
				</tr>
			</thead>
			<tbody>
				<xsl:for-each select="ReferenceToDocumentId">
					<xsl:variable name="Step" select="position()"/>
					<xsl:for-each select="key('DocumentsInfoById',.)">
						<xsl:call-template name="DocumentFilesTable">
							<xsl:with-param name="Pos"><xsl:value-of select="$Step"/></xsl:with-param>
						</xsl:call-template>
					</xsl:for-each>
				</xsl:for-each>
			</tbody>
		</table>
	</xsl:template>

	<xsl:template name="EngineeringSurveyDocumentTable">
		<xsl:param name="Obj"/>
		<tr>
			<td colspan="2" class="not-border upper bold">
				<xsl:variable name="SurveyDocumentName">
					<xsl:call-template name="DocumentTypeList">
						<xsl:with-param name="Code" select="$Obj/@Type"/>
					</xsl:call-template>
				</xsl:variable>
				<xsl:value-of select="substring-after($SurveyDocumentName, '.' )"/>
			</td>
		</tr>
		<xsl:if test="$Obj/Name">
			<tr>
				<td>Наименование документа:</td>
				<td><xsl:value-of select="$Obj/Name"/></td>
			</tr>
		</xsl:if>
		
		<tr>
			<td>Требования к документу:</td>
			<td>
				<xsl:if test="$Obj/Requirements/@Title">
					<h5><xsl:value-of select="$Obj/Requirements/@Title"/></h5>
				</xsl:if>
				<xsl:apply-templates select="$Obj/Requirements/*"/>
			</td>
		</tr>
		<xsl:if test="Norms">
			<xsl:variable name="cntNorms" select="count($Obj/Norms/Norm)"/>
			<xsl:for-each select="$Obj/Norms/Norm">
				<tr>
					<xsl:if test="position()=1">
						<td width="25%">
							<xsl:attribute name="rowspan">
								<xsl:value-of select="$cntNorms"/>
							</xsl:attribute>
							Перечень нормативных требований:
						</td>
					</xsl:if>
					<td><xsl:value-of select="."/></td>
				</tr>
			</xsl:for-each>
		</xsl:if>
	</xsl:template>
	
	<xsl:template name="ObjectTEI">
		<a name="ch10"/>
		<h3 class="bckgr upper">10. Требования к основным технико-экономическим показателям</h3>
		
		<xsl:if test="/Document/Content/Object/ObjectParts">
			<h4 class="upper under bold">10.1. Основные технико-экономические показатели объекта капитального строительства:</h4>
		</xsl:if>
		
		<xsl:call-template name="POITEI">
			<xsl:with-param name="Obj" select="/Document/Content/Object/POI"></xsl:with-param>
		</xsl:call-template>
		<xsl:call-template name="POITEI">
			<xsl:with-param name="Obj" select="/Document/Content/Object/TEI"></xsl:with-param>
		</xsl:call-template>	

		<xsl:if test="/Document/Content/Object/ObjectParts">
			<h4 class="upper under bold">10.2. Основные технико-экономические показатели объектов капитального строительства, входящих в состав:</h4>
			<xsl:apply-templates select="/Document/Content/Object/ObjectParts">
				<xsl:with-param name="level" select="1."/>
				<xsl:with-param name="show" select="1"/>
			</xsl:apply-templates>
		</xsl:if>
	</xsl:template>
		
	<xsl:template name="POITEI">
		<xsl:param name="Obj"/>
		<xsl:variable name="OLD" select="$Obj//OldValue or $Obj//OldMinValue"/>
		
		<xsl:if test="count($Obj)!=0">
			<table>
				<thead>
					<tr class="bold center">
						<th rowspan="2" width="50%">
							<xsl:if test="$Obj[name()='POI']">Наименование показателя мощности</xsl:if>
							<xsl:if test="$Obj[name()='TEI']">Наименование технико-экономического показателя</xsl:if>
						</th>
						<th rowspan="2" width="12%">Единица измерения показателя</th>
						<th colspan="2" width="38%">
							<xsl:if test="$OLD">
								<xsl:attribute name="width">19%</xsl:attribute>
							</xsl:if>
							Значение показателя</th>
						<xsl:if test="$OLD">
							<th colspan="2">Предыдущее<br/>значение показателя</th>
						</xsl:if>
					</tr>
					<tr class="bold center">
						<th width="19%" title="Минимальное значение">
							<xsl:if test="$OLD">
								<xsl:attribute name="width">9%</xsl:attribute>
							</xsl:if>Мин</th>
						<th width="19%" title="Максимальное значение">
							<xsl:if test="$OLD">
								<xsl:attribute name="width">9%</xsl:attribute>
							</xsl:if>Макс</th>
						<xsl:if test="$OLD">
							<th title="Минимальное значение">Мин</th>
							<th title="Максимальное значение">Макс</th>
						</xsl:if>
					</tr>
				</thead>
				<tbody>
				<xsl:for-each select="$Obj">
					<xsl:for-each select=".">
						<tr class="center">
							<td class="left"><xsl:value-of select="Name"/></td>
							<td>
								<xsl:if test="Measure='' or not(Measure)">-</xsl:if>
								<xsl:apply-templates select="Measure"/>
							</td>
							<xsl:if test="MinValue">
								<td><xsl:value-of select="MinValue"/></td>
								<td><xsl:value-of select="MaxValue"/></td>
							</xsl:if>
							<xsl:if test="Value">
								<td colspan="2"><xsl:value-of select="Value"/></td>
							</xsl:if>
							
							<xsl:if test="$OLD">
								<xsl:choose>
									<xsl:when test="OldMinValue">
										<td><xsl:value-of select="OldMinValue"/></td>
										<td><xsl:value-of select="OldMaxValue"/></td>
									</xsl:when>
									<xsl:when test="OldValue">
										<td colspan="2"><xsl:value-of select="OldValue"/></td>
									</xsl:when>
									<xsl:otherwise>
										<td colspan="2">Отсутствует</td>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:if>
						</tr>
					</xsl:for-each>
				</xsl:for-each></tbody>
			</table>
		</xsl:if>
	</xsl:template>
	
	<xsl:template name="SpecialConditions">
		<a name="ch19"/>
		<h3 class="bckgr upper">19. Особые условия строительства</h3>

		<h4 class="upper under">19.1. Общие сведения:</h4>
		<table>
			<xsl:if test="/Document/Content/Land/Common">
				<tr>
					<td  width="25%">Общие сведения о земельных участках:</td>
					<td>
						<xsl:call-template name="TextBlockNotInTable">
							<xsl:with-param name="obj" select="/Document/Content/Land/Common"/>
						</xsl:call-template>
					</td>
				</tr>	
			</xsl:if>

			<xsl:for-each select="/Document/Content/Land/LandCategories/*">
				<xsl:if test="position()=1">
					<tr>
						<td>
							<xsl:attribute name="rowspan"><xsl:value-of select="count(/Document/Content/Land/LandCategories/LandCategory)"/></xsl:attribute>
							Сведения о категории земель, на которых располагается (будет располагаться) объект:
						</td>
						<td><xsl:apply-templates select="."/></td>
					</tr>
				</xsl:if>
				<xsl:if test="position()!=1">
					<tr><td><xsl:apply-templates select="."/></td></tr>
				</xsl:if>
			</xsl:for-each>

			<xsl:for-each select="/Document/Content/ClimateConditions">
				<tr>
					<td  width="25%">Общие сведения о климатической, географической и инженерно-геологической характеристике района:</td>
					<td>
						<xsl:call-template name="TextBlockNotInTable">
							<xsl:with-param name="obj" select="Common"/>
						</xsl:call-template>
					</td>
				</tr>
				
				<tr>
					<td>Возможность опасных природных процессов, явлений и техногенных воздействий:</td>
					<td>
						<xsl:call-template name="TextBlockNotInTable">
							<xsl:with-param name="obj" select="DangerousNatureProcesses"/>
						</xsl:call-template>
						<xsl:if test="not(DangerousNatureProcesses)">
							Сведения отсутствуют
						</xsl:if>
					</td>
				</tr>
			
				<xsl:if test="ClimateDistrict">
					<tr>
						<td>Климатический район, подрайон:</td>
						<td>
							<xsl:for-each select="ClimateDistrict">
								<xsl:value-of select="."/>
								<xsl:if test="position() != last()">, </xsl:if>
							</xsl:for-each>
						</td>
					</tr>
				</xsl:if>
				<xsl:if test="GeologicalConditions">
					<tr>
						<td>Категория сложности инженерно-геологических(геокриологических) условий:</td>
						<td>
							<xsl:for-each select="GeologicalConditions">
								<xsl:value-of select="."/>
								<xsl:if test="position() != last()">, </xsl:if>
							</xsl:for-each>
						</td>
					</tr>
				</xsl:if>
				<xsl:if test="WindDistrict">
					<tr>
						<td>Ветровой район:</td>
						<td>
							<xsl:for-each select="WindDistrict">
								<xsl:value-of select="."/>
								<xsl:if test="position() != last()">, </xsl:if>
							</xsl:for-each>
						</td>
					</tr>
				</xsl:if>
				<xsl:if test="SnowDistrict">
					<tr>
						<td>Снеговой район:</td>
						<td>
							<xsl:for-each select="SnowDistrict">
								<xsl:value-of select="."/>
								<xsl:if test="position() != last()">, </xsl:if>
							</xsl:for-each>
						</td>
					</tr>
				</xsl:if>
				<xsl:if test="SeismicActivity">
					<tr>
						<td>Интенсивность сейсмических воздействий:</td>
						<td>
							<xsl:for-each select="SeismicActivity">
								<xsl:value-of select="."/>
								<xsl:if test="position() != last()">, </xsl:if>
							</xsl:for-each>
						</td>
					</tr>
				</xsl:if>
							
			</xsl:for-each>
		</table>
		
		<xsl:for-each select="/Document/Content/Land/SeizureLandAreasInfo">
			<xsl:if test="position()=1">
				<h4 class="upper under">19.2. Сведения о земельных участках, изымаемых для государственных или муниципальных нужд, о земельных участках, в отношении которых устанавливается сервитут, публичный сервитут и (или) заключается договор аренды (субаренды), - в случае изъятия земельного участка для государственных или муниципальных нужд, установления сервитута, публичного сервитута, заключения договора аренды (субаренды):</h4>
			</xsl:if>
			<table>
				<tr>
					<td colspan="3">
						<xsl:for-each select="Common">
							<xsl:if test="@Title">
								<h5><xsl:value-of select="@Title"/></h5>
							</xsl:if>
							<xsl:apply-templates select="."/>
						</xsl:for-each>
					</td>
				</tr>
				<xsl:if test="SeizureLandAreaInfo">
					<tr class="bold center">
						<td width="25%">Кадастровый номер участка</td>
						<td width="25%">Категория земель</td>
						<td>Обоснования действия с земельным участком (изъятие, установление сервитута и пр.), дополнительные сведения</td>
					</tr>
					<xsl:for-each select="SeizureLandAreaInfo">
						<tr>
							<td><xsl:value-of select="CadastralNumber"/></td>
							<td><xsl:apply-templates select="LandCategory"/></td>
							<td><xsl:value-of select="UsingNote"/></td>
						</tr>
					</xsl:for-each>
				</xsl:if>
			</table>
		</xsl:for-each>
	</xsl:template>
		
	<xsl:template match="LandCategory">
		<xsl:choose>
			<xsl:when test=". = 1">Земли сельскохозяйственного назначения</xsl:when>
			<xsl:when test=". = 2">Земли населенных пунктов</xsl:when>
			<xsl:when test=". = 3">Земли промышленности, энергетики, транспорта, связи, радиовещания, телевидения, информатики, земли для обеспечения космической деятельности, земли обороны, безопасности и земли иного специального назначения</xsl:when>
			<xsl:when test=". = 4">Земли особо охраняемых территорий и объектов</xsl:when>
			<xsl:when test=". = 5">Земли лесного фонда</xsl:when>
			<xsl:when test=". = 6">Земли водного фонда</xsl:when>
			<xsl:when test=". = 7">Земли запаса</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template name="Stages">
		<a name="ch7"/>
		<h3 class="bckgr upper">7. Требования к выделению этапов строительства объекта</h3>
		
		<xsl:for-each select="/Document/Content/Stages">
			<table><tr><td>
				<xsl:for-each select="Common">
					<xsl:if test="@Title">
						<h5><xsl:value-of select="@Title"/></h5>
					</xsl:if>
					<xsl:apply-templates select="."/>
				</xsl:for-each>
			</td></tr></table>
			<xsl:if test="Stage">
				<table>
					<thead>
						<tr>
							<th width="30%">Номер или наименование этапа</th>
							<th width="15%">Дата начала этапа</th>
							<th width="15%">Дата окончания этапа</th>
							<th width="15%">Дата ввода в<br/>эксплуатацию<br/>(при наличии)</th>
							<th width="25%">Примечание</th>
						</tr>
					</thead>
					<tbody>
						<xsl:for-each select="Stage">
							<tr class="center">
								<td class="left">
									<xsl:value-of select="Name"/>
								</td>
								<td>
									<xsl:if test="not(BeginDate)">-</xsl:if>
									<xsl:call-template name="FormatDate">
										<xsl:with-param name="DateTimeStr" select="BeginDate"/>
									</xsl:call-template>
								</td>
								<td>
									<xsl:if test="not(EndDate)">-</xsl:if>
									<xsl:call-template name="FormatDate">
										<xsl:with-param name="DateTimeStr" select="EndDate"/>
									</xsl:call-template>
								</td>
								<td>
									<xsl:if test="not(OperationDate)">-</xsl:if>
									<xsl:call-template name="FormatDate">
										<xsl:with-param name="DateTimeStr" select="OperationDate"/>
									</xsl:call-template>
								</td>
								<td class="left">
									<xsl:if test="not(Note)">Отсутствует</xsl:if>
									<xsl:value-of select="Note"/>
								</td>
							</tr>
						</xsl:for-each>
					</tbody>
				</table>
			</xsl:if>
		</xsl:for-each>
		<xsl:if test="not(/Document/Content/Stages)">
			<table><tr><td>Необходимость выделения этапов строительства отсутствует</td></tr></table>
		</xsl:if>
	</xsl:template>

	<xsl:template match="InitialDocuments">
		<a name="ch50"/>
		<h3 class="bckgr upper">50. Материалы, предоставляемые застройщиком (техническим заказчиком)</h3>
		<table>
			<xsl:if test="count(DocumentInfo[File]) > 0">
				<thead>
					<tr class="bold center">
						<td width="5%">№ п/п</td>
						<td width="65%">Наименование и реквизиты документа</td>
						<td width="25%">Наименование файла документа (подписи документа)</td>
						<td>Контрольная сумма файла</td>
					</tr>
				</thead>
			</xsl:if>
			<tbody>
				<xsl:for-each select="DocumentInfo">
					<xsl:sort select="@Type"/>
					<xsl:call-template name="DocumentFilesTable"/>
				</xsl:for-each>
			</tbody>
		</table>
		<xsl:if test="Note">
			<p class="upper bold under">Дополнительные сведения:</p>
			<table><tr><td><xsl:value-of select="Note"/></td></tr></table>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Agreements">
		<a name="ch49"/>
		<h3 class="bckgr upper">49. Перечень необходимых согласований</h3>
		<table>
			<xsl:for-each select="/Document/Content/Agreements/Agreement">
				<tr><td width="5%"><xsl:number value="position()" format="1. "/></td>
					<td><xsl:value-of select="."/></td>
				</tr>
			</xsl:for-each>
			<xsl:if test="not(/Document/Content/Agreements)">
				<tr><td><p>Требования отсутствуют</p></td></tr>
			</xsl:if>
		</table>
	</xsl:template>
	
	<xsl:template name="SurveyTypeList">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code = '06.01' or $Code = 1">Инженерно-геодезические изыскания</xsl:when>
			<xsl:when test="$Code = '06.02' or $Code = 2">Инженерно-геологические изыскания</xsl:when>
			<xsl:when test="$Code = '06.03' or $Code = 3">Инженерно-гидрометеорологические изыскания</xsl:when>
			<xsl:when test="$Code = '06.04' or $Code = 4">Инженерно-экологические изыскания</xsl:when>
			<xsl:when test="$Code = '06.05' or $Code = 5">Инженерно-геотехнические изыскания</xsl:when>
			<xsl:when test="$Code = '06.06' or $Code = 6">Геотехнические исследования</xsl:when>
			<xsl:when test="$Code = '06.07' or $Code = 7">Обследования состояния грунтов оснований зданий и сооружений, их строительных конструкций</xsl:when>
			<xsl:when test="$Code = '06.08' or $Code = 8">Поиск и разведка подземных вод для целей водоснабжения</xsl:when>
			<xsl:when test="$Code = '06.09' or $Code = 9">Локальный мониторинг компонентов окружающей среды</xsl:when>
			<xsl:when test="$Code = '06.010' or $Code = 10">Разведка грунтовых строительных материалов</xsl:when>
			<xsl:when test="$Code = '06.011' or $Code = 11">Локальные обследования загрязнения грунтов и грунтовых вод</xsl:when>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="SurveySpecialTypeList">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code = 1">Карстологические исследования</xsl:when>
			<xsl:when test="$Code = 2">Сейсмическое микрорайонирование</xsl:when>
			<xsl:when test="$Code = 3">Археологические изыскания</xsl:when>
			<xsl:when test="$Code = 4">Геоботанические исследования</xsl:when>
			<xsl:when test="$Code = 5">Математическое моделирование. Расчет гидрологических характеристик</xsl:when>
			<xsl:when test="$Code = 6">Геолого-разведочные работы</xsl:when>
			<xsl:when test="$Code = 7">Оценка территории распространения многолетнемерзлых грунтов по степени благоприятности для строительного освоения</xsl:when>
			<xsl:when test="$Code = 8">Воздушное лазерное сканирование</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template name="DocumentTypeList">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code = '01.01'">Документы-основания проведения экспертизы. Заявление о проведении экспертизы</xsl:when>
			<xsl:when test="$Code = '01.02'">Документы-основания проведения экспертизы. Договор о проведении экспертизы</xsl:when>
			<xsl:when test="$Code = '01.03'">Документы-основания проведения экспертизы. Документ, подтверждающий полномочия заявителя действовать от имени застройщика, технического заказчика, лица, обеспечившего выполнение инженерных изысканий и (или) подготовку проектной документации в случаях, предусмотренных частями 1.1 и 1.2 статьи 48 Градостроительного кодекса Российской Федерации</xsl:when>
			<xsl:when test="$Code = '01.99'">Документы-основания проведения экспертизы. Иные документы</xsl:when>
			<xsl:when test="$Code = '02.01'">Заключение экспертизы. Заключение экспертизы проектной документации и/или результатов инженерных изысканий, выданное ранее в отношении этого же объекта</xsl:when>
			<xsl:when test="$Code = '02.02'">Заключение экспертизы. Заключение по результатам оценки соответствия в рамках экспертного сопровождения</xsl:when>
			<xsl:when test="$Code = '02.04'">Заключение экспертизы. Заключение государственной экологической экспертизы</xsl:when>
			<xsl:when test="$Code = '02.05'">Заключение экспертизы. Заключение государственной историко-культурной экспертизы</xsl:when>
			<xsl:when test="$Code = '02.06'">Заключение экспертизы. Сводное заключение о проведении публичного технологического аудита крупного инвестиционного проекта с государственным участием</xsl:when>
			<xsl:when test="$Code = '02.07'">Заключение экспертизы. Заключение технологического и ценового аудита обоснования инвестиций</xsl:when>
			<xsl:when test="$Code = '02.08'">Заключение экспертизы. Заключение государственной экспертизы запасов подземных вод</xsl:when>
			<xsl:when test="$Code = '02.09'">Заключение экспертизы. Заключение государственной экспертизы запасов полезных ископаемых</xsl:when>
			<xsl:when test="$Code = '02.99'">Заключение экспертизы. Иные заключения</xsl:when>
			<xsl:when test="$Code = '03.01'">Документы размещения объекта строительства. Документ территориального планирования</xsl:when>
			<xsl:when test="$Code = '03.02'">Документы размещения объекта строительства. Градостроительный план земельного участка</xsl:when>
			<xsl:when test="$Code = '03.03'">Документы размещения объекта строительства. Проект планировки территории</xsl:when>
			<xsl:when test="$Code = '03.04'">Документы размещения объекта строительства. Проект межевания территории</xsl:when>
			<xsl:when test="$Code = '03.05'">Документы размещения объекта строительства. Согласование включения в границы территории, подлежащей комплексному развитию по инициативе правообладателей земельных участков, для размещения объектов коммунальной, транспортной, социальной инфраструктур, находящихся в государственной и (или) муниципальной собственности и не обремененных правами третьих лиц</xsl:when>
			<xsl:when test="$Code = '03.06'">Документы размещения объекта строительства. Согласование при осуществлении строительства помещений и сооружений, необходимых для организации пограничного, таможенного и иных видов контроля в пункте пропуска через Государственную границу</xsl:when>
			<xsl:when test="$Code = '03.99'">Документы размещения объекта строительства. Иные документы</xsl:when>
			<xsl:when test="$Code = '04.01'">Документы подключения объекта строительства к инженерным сетям. Технические условия на подключение объекта капитального строительства к сетям инженерно-технического обеспечения</xsl:when>
			<xsl:when test="$Code = '04.02'">Документы подключения объекта строительства к инженерным сетям. Документ о согласовании отступлений от положений технических условий</xsl:when>
			<xsl:when test="$Code = '04.03'">Документы подключения объекта строительства к инженерным сетям. Технические условия на перенос и переустройство линий связи и сооружений связи</xsl:when>
			<xsl:when test="$Code = '04.99'">Документы подключения объекта строительства к инженерным сетям. Иные документы</xsl:when>
			<xsl:when test="$Code = '05.01'">Задания и программы. Задание на проведение инженерных изысканий</xsl:when>
			<xsl:when test="$Code = '05.02'">Задания и программы. Программа инженерных изысканий</xsl:when>
			<xsl:when test="$Code = '05.03'">Задания и программы. Задание на проектирование</xsl:when>
			<xsl:when test="$Code = '05.99'">Задания и программы. Иные задания</xsl:when>
			<xsl:when test="$Code = '06.01'">Результаты инженерных изысканий. Инженерно-геодезические изыскания</xsl:when>
			<xsl:when test="$Code = '06.02'">Результаты инженерных изысканий. Инженерно-геологические изыскания</xsl:when>
			<xsl:when test="$Code = '06.03'">Результаты инженерных изысканий. Инженерно-гидрометеорологические изыскания</xsl:when>
			<xsl:when test="$Code = '06.04'">Результаты инженерных изысканий. Инженерно-экологические изыскания</xsl:when>
			<xsl:when test="$Code = '06.05'">Результаты инженерных изысканий. Инженерно-геотехнические изыскания</xsl:when>
			<xsl:when test="$Code = '06.06'">Результаты инженерных изысканий. Геотехнические исследования</xsl:when>
			<xsl:when test="$Code = '06.07'">Результаты инженерных изысканий. Обследования состояния грунтов оснований зданий и сооружений, их строительных конструкций</xsl:when>
			<xsl:when test="$Code = '06.08'">Результаты инженерных изысканий. Поиск и разведка подземных вод для целей водоснабжения</xsl:when>
			<xsl:when test="$Code = '06.09'">Результаты инженерных изысканий. Локальный мониторинг компонентов окружающей среды</xsl:when>
			<xsl:when test="$Code = '06.10'">Результаты инженерных изысканий. Разведка грунтовых строительных материалов</xsl:when>
			<xsl:when test="$Code = '06.11'">Результаты инженерных изысканий. Локальные обследования загрязнения грунтов и грунтовых вод</xsl:when>
			<xsl:when test="$Code = '06.99'">Результаты инженерных изысканий. Иной документ</xsl:when>
			<xsl:when test="$Code = '07.01'">Проектная документация. Раздел 1. «Пояснительная записка» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.02'">Проектная документация. Раздел 2. «Схема планировочной организации земельного участка» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.03'">Проектная документация. Раздел 3. «Архитектурные решения» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.04'">Проектная документация. Раздел 4. «Конструктивные и объемно-планировочные решения» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.05'">Проектная документация. Раздел 5. Подраздел «Система электроснабжения» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.06'">Проектная документация. Раздел 5. Подраздел «Система водоснабжения» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.07'">Проектная документация. Раздел 5. Подраздел «Система водоотведения» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.08'">Проектная документация. Раздел 5. Подраздел «Отопление, вентиляция и кондиционирование воздуха, тепловые сети» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.09'">Проектная документация. Раздел 5. Подраздел «Сети связи» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.10'">Проектная документация. Раздел 5. Подраздел «Система газоснабжения» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.11'">Проектная документация. Раздел 5. Подраздел «Технологические решения» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.12'">Проектная документация. Раздел 6. «Проект организации строительства» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.13'">Проектная документация. Раздел 7. «Проект организации работ по сносу или демонтажу объектов капитального строительства» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.14'">Проектная документация. Раздел 8. «Перечень мероприятий по охране окружающей среды» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.15'">Проектная документация. Раздел 9. «Мероприятия по обеспечению пожарной безопасности» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.16'">Проектная документация. Раздел 10. «Мероприятия по обеспечению доступа инвалидов» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.17'">Проектная документация. Раздел 10.1. «Мероприятия по обеспечению соблюдения требований энергетической эффективности и требований оснащенности зданий, строений и сооружений приборами учета используемых энергетических ресурсов» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.18'">Проектная документация. Раздел 11. «Смета на строительство объектов капитального строительства» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.19'">Проектная документация. Раздел 12. «Иная документация в случаях, предусмотренных федеральными законами» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.20'">Проектная документация. Раздел 1. «Пояснительная записка» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.21'">Проектная документация. Раздел 2. «Схема планировочной организации земельного участка» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.22'">Проектная документация. Раздел 3. «Объемно-планировочные и архитектурные решения» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.23'">Проектная документация. Раздел 4. «Конструктивные решения» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.24'">Проектная документация. Раздел 5. Подраздел «Система электроснабжения» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.25'">Проектная документация. Раздел 5. Подраздел «Система водоснабжения» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.26'">Проектная документация. Раздел 5. Подраздел «Система водоотведения» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.27'">Проектная документация. Раздел 5. Подраздел «Отопление, вентиляция и кондиционирование воздуха, тепловые сети» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.28'">Проектная документация. Раздел 5. Подраздел «Сети связи» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.29'">Проектная документация. Раздел 5. Подраздел «Система газоснабжения» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.30'">Проектная документация. Раздел 6. «Технологические решения» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.31'">Проектная документация. Раздел 7. «Проект организации строительства» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.32'">Проектная документация. Раздел 8. «Мероприятия по охране окружающей среды» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.33'">Проектная документация. Раздел 9. «Мероприятия по обеспечению пожарной безопасности» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.34'">Проектная документация. Раздел 10. «Требования к обеспечению безопасной эксплуатации объектов капитального строительства» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.35'">Проектная документация. Раздел 11. «Мероприятия по обеспечению доступа инвалидов к объекту капитального строительства» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.36'">Проектная документация. Раздел 12. «Смета на строительство, реконструкцию, капитальный ремонт, снос объекта капитального строительства» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '07.37'">Проектная документация. Раздел 13. «Иная документация в случаях, предусмотренных законодательными и иными нормативными правовыми актами Российской Федерации» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.01'">Проектная документация. Линейный объект. Раздел 1. «Пояснительная записка» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.02'">Проектная документация. Линейный объект. Раздел 2. «Проект полосы отвода» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.03'">Проектная документация. Линейный объект. Раздел 3. «Технологические и конструктивные решения линейного объекта. Искусственные сооружения» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.04'">Проектная документация. Линейный объект. Раздел 4. «Здания, строения и сооружения, входящие в инфраструктуру линейного объекта» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.05'">Проектная документация. Линейный объект. Раздел 5. «Проект организации строительства» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.06'">Проектная документация. Линейный объект. Раздел 6. «Проект организации работ по сносу (демонтажу) линейного объекта» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.07'">Проектная документация. Линейный объект. Раздел 7. «Мероприятия по охране окружающей среды» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.08'">Проектная документация. Линейный объект. Раздел 8. «Мероприятия по обеспечению пожарной безопасности» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.09'">Проектная документация. Линейный объект. Раздел 9. «Смета на строительство» (действовал до 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.10'">Проектная документация. Линейный объект. Раздел 10. «Иная документация в случаях, предусмотренных федеральными законами» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.11'">Проектная документация. Линейный объект. Раздел 1. «Пояснительная записка» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.12'">Проектная документация. Линейный объект. Раздел 2. «Проект полосы отвода» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.13'">Проектная документация. Линейный объект. Раздел 3. «Технологические и конструктивные решения линейного объекта. Искусственные сооружения» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.14'">Проектная документация. Линейный объект. Раздел 4. «Здания, строения и сооружения, входящие в инфраструктуру линейного объекта» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.15'">Проектная документация. Линейный объект. Раздел 5. «Проект организации строительства» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.16'">Проектная документация. Линейный объект. Раздел 6. «Мероприятия по охране окружающей среды» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.17'">Проектная документация. Линейный объект. Раздел 7. «Мероприятия по обеспечению пожарной безопасности» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.18'">Проектная документация. Линейный объект. Раздел 8. «Требования к обеспечению безопасной эксплуатации линейного объекта» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.19'">Проектная документация. Линейный объект. Раздел 9. «Смета на строительство, реконструкцию, капитальный ремонт, снос объекта капитального строительства» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '08.20'">Проектная документация. Линейный объект. Раздел 10. «Иная документация в случаях, предусмотренных законодательными и иными нормативными правовыми актами Российской Федерации» (действует с 01.09.2022)</xsl:when>
			<xsl:when test="$Code = '09.01'">Переписка по вопросам проведения экспертизы. Уведомление о выявлении недостатков</xsl:when>
			<xsl:when test="$Code = '09.02'">Переписка по вопросам проведения экспертизы. Сопроводительное письмо заявителя с откорректированной проектной документацией</xsl:when>
			<xsl:when test="$Code = '09.99'">Переписка по вопросам проведения экспертизы. Иной документ</xsl:when>
			<xsl:when test="$Code = '10.01'">Документы о членстве в саморегулируемой организации. Выписка из реестра членов саморегулируемой организации</xsl:when>
			<xsl:when test="$Code = '10.99'">Документы о членстве в саморегулируемой организации. Иной документ</xsl:when>
			<xsl:when test="$Code = '11.01'">Документы для проведения проверки достоверности определения сметной стоимости. Ведомость объемов работ</xsl:when>
			<xsl:when test="$Code = '11.02'">Документы для проведения проверки достоверности определения сметной стоимости. Решение по объекту капитального строительства</xsl:when>
			<xsl:when test="$Code = '11.03'">Документы для проведения проверки достоверности определения сметной стоимости. Акт, содержащий перечень дефектов оснований, строительных конструкций, систем инженерно-технического обеспечения и сетей инженерно-технического обеспечения</xsl:when>
			<xsl:when test="$Code = '11.04'">Документы для проведения проверки достоверности определения сметной стоимости. Решение о разработке и применении индивидуальных сметных нормативов</xsl:when>
			<xsl:when test="$Code = '11.05'">Документы для проведения проверки достоверности определения сметной стоимости. Коньюктурный анализ</xsl:when>
			<xsl:when test="$Code = '11.06'">Документы для проведения проверки достоверности определения сметной стоимости. Прайс-лист</xsl:when>
			<xsl:when test="$Code = '11.99'">Документы для проведения проверки достоверности определения сметной стоимости. Иной документ</xsl:when>
			<xsl:when test="$Code = '12.01'">Документы в отношении экономически эффективной (типовой) проектной документации повторного использования. Положительное заключение экспертизы в отношении экономически эффективной (типовой) проектной документации повторного использования</xsl:when>
			<xsl:when test="$Code = '12.02'">Документы в отношении экономически эффективной (типовой) проектной документации повторного использования. Справка с указанием разделов, которые не подвергались изменению</xsl:when>
			<xsl:when test="$Code = '12.03'">Документы в отношении экономически эффективной (типовой) проектной документации повторного использования. Документ, подтверждающий аналогичность</xsl:when>
			<xsl:when test="$Code = '12.99'">Документы в отношении экономически эффективной (типовой) проектной документации повторного использования. Иной документ</xsl:when>
			<xsl:when test="$Code = '13.01'">Документы в отношении работ по сносу объектов капитального строительства. Проект организации работ по сносу объекта капитального строительства</xsl:when>
			<xsl:when test="$Code = '13.02'">Документы в отношении работ по сносу объектов капитального строительства. Смета на снос объекта капитального строительства</xsl:when>
			<xsl:when test="$Code = '13.03'">Документы в отношении работ по сносу объектов капитального строительства. Акт (решение) собственника здания (сооружения, строения) о выведении из эксплуатации и ликвидации объекта капитального строительства</xsl:when>
			<xsl:when test="$Code = '13.04'">Документы в отношении работ по сносу объектов капитального строительства. Решение федерального органа исполнительной власти, органа исполнительной власти субъекта Российской Федерации или органа местного самоуправления о признании многоквартирного дома аварийным и подлежащим сносу</xsl:when>
			<xsl:when test="$Code = '13.05'">Результаты и материалы обследования объекта капитального строительства в соответствии с требованиями технических регламентов, санитарно-эпидемиологическими требованиями, требованиями в области охраны окружающей среды, требованиями безопасности деятельности в области использования атомной энергии, требованиями к осуществлению деятельности в области промышленной безопасности</xsl:when>
			<xsl:when test="$Code = '13.06'">Документ, подтверждающий передачу проекта организации работ по сносу объекта капитального строительства застройщику, техническому заказчику или лицу, обеспечившему выполнение инженерных изысканий и (или) подготовку проектной документации</xsl:when>
			<xsl:when test="$Code = '13.99'">Документы в отношении работ по сносу объектов капитального строительства. Иной документ</xsl:when>
			<xsl:when test="$Code = '14.01'">Программы развития. Федеральная целевая программа</xsl:when>
			<xsl:when test="$Code = '14.02'">Программы развития. Программа развития субъекта Российской Федерации</xsl:when>
			<xsl:when test="$Code = '14.03'">Программы развития. Программа развития муниципального образования</xsl:when>
			<xsl:when test="$Code = '14.04'">Программы развития. Ведомственная целевая программа</xsl:when>
			<xsl:when test="$Code = '14.99'">Программы развития. Иная программа</xsl:when>
			<xsl:when test="$Code = '15.01'">Решение о разработке проектной документации. Решение Президента Российской федерации</xsl:when>
			<xsl:when test="$Code = '15.02'">Решение о разработке проектной документации. Нормативный правовой акт Правительства Российской Федерации</xsl:when>
			<xsl:when test="$Code = '15.03'">Решение о разработке проектной документации. Нормативный правовой акт высшего органа исполнительной власти субъекта Российской Федерации</xsl:when>
			<xsl:when test="$Code = '15.04'">Решение о разработке проектной документации. Муниципальный правовой акт местной администрации муниципального образования</xsl:when>
			<xsl:when test="$Code = '15.05'">Решение о разработке проектной документации. Решение главного распорядителя средств федерального бюджета о подготовке и реализации бюджетных инвестиций, о предоставлении субсидий на осуществление капитальных вложений в объект капитального строительства</xsl:when>
			<xsl:when test="$Code = '15.06'">Решение о разработке проектной документации. Решение руководителя государственной компании и корпорации об осуществлении капитальных вложений в объект капитального строительства</xsl:when>
			<xsl:when test="$Code = '15.07'">Решение о разработке проектной документации. Решение по объекту капитального строительства, принятое в порядке, установленном методикой, приведенной в приложении к соответствующей федеральной целевой программе, определяющей порядок детализации мероприятий (укрупненных инвестиционных проектов), содержащее информацию об объекте капитального строительства, входящем в мероприятие (укрупненный инвестиционный проект)</xsl:when>
			<xsl:when test="$Code = '15.08'">Решение о разработке проектной документации. Решение застройщика</xsl:when>
			<xsl:when test="$Code = '15.99'">Решение о разработке проектной документации. Решение иного лица</xsl:when>
			<xsl:when test="$Code = '16.01'">Международные договоры. Международный договор</xsl:when>
			<xsl:when test="$Code = '16.02'">Международные договоры. Соглашение о разделе продукции</xsl:when>
			<xsl:when test="$Code = '16.99'">Международные договоры. Иные договоры</xsl:when>
			<xsl:when test="$Code = '17.01'">Правоустанавливающие документы. Выписка из Единого государственного реестра недвижимости</xsl:when>
			<xsl:when test="$Code = '17.99'">Правоустанавливающие документы. Иной правоустанавливающий документ</xsl:when>
			<xsl:when test="$Code = '18.01'">Документы о безопасности производственных объектов. Обоснование безопасности опасного производственного объекта в случаях, предусмотренных частью 4 статьи 3 Федерального закона «О промышленной безопасности опасных производственных объектов»</xsl:when>
			<xsl:when test="$Code = '18.02'">Документы о безопасности производственных объектов. Положительное заключение экспертизы промышленной безопасности такого обоснования, внесенное в реестр заключений экспертизы промышленной безопасности</xsl:when>
			<xsl:when test="$Code = '18.03'">Документы о безопасности производственных объектов. Документ о регистрации в государственном реестре опасных производственных объектов</xsl:when>
			<xsl:when test="$Code = '18.99'">Документы о безопасности производственных объектов. Иные документы</xsl:when>
			<xsl:when test="$Code = '19.01'">Специальные технические условия. Специальные технические условия</xsl:when>
			<xsl:when test="$Code = '19.02'">Специальные технические условия. Документ о согласовании отступлений от положений специальных технических условий</xsl:when>
			<xsl:when test="$Code = '19.03'">Специальные технические условия. Технические требования и условия, подлежащие обязательному исполнению при подготовке проектной документации в целях реконструкции, капитального ремонта существующих линейного объекта или линейных объектов, а также при осуществлении таких реконструкций, капитального ремонта</xsl:when>
			<xsl:when test="$Code = '19.99'">Специальные технические условия. Иные документы</xsl:when>
			<xsl:when test="$Code = '20.01'">Разрешения. Разрешение на строительство</xsl:when>
			<xsl:when test="$Code = '20.02'">Разрешения. Разрешение на ввод объектов в эксплуатацию</xsl:when>
			<xsl:when test="$Code = '20.03'">Разрешения. Акт освидетельствования проведения основных работ по строительству, реконструкции</xsl:when>
			<xsl:when test="$Code = '20.04'">Разрешения. Разрешение на условно разрешенный вид использования земельного участка или объекта капитального строительства</xsl:when>
			<xsl:when test="$Code = '20.05'">Разрешения. Разрешение на отклонение от предельных параметров разрешенного строительства, реконструкции объектов капитального строительства</xsl:when>
			<xsl:when test="$Code = '20.06'">Разрешения. Разрешение на застройку земельных участков, которые расположены за границами населенных пунктов и находятся на площадях залегания полезных ископаемых, а также на размещение за границами населенных пунктов в местах залегания полезных ископаемых подземных сооружений в пределах горного отвода</xsl:when>
			<xsl:when test="$Code = '20.07'">Разрешения. Разрешение на установку радиопередающих средств на высотных зданиях</xsl:when>
			<xsl:when test="$Code = '20.99'">Разрешения. Иные разрешения</xsl:when>
			<xsl:when test="$Code = '21.01'">Документы в сфере охраны окружающей среды и недропользования. Расчет нормативов допустимых выбросов, нормативов допустимых сбросов</xsl:when>
			<xsl:when test="$Code = '21.02'">Документы в сфере охраны окружающей среды и недропользования. Горноотводный акт с планом границ горного отвода или его копия</xsl:when>
			<xsl:when test="$Code = '21.03'">Документы в сфере охраны окружающей среды и недропользования. Лицензия на пользование недрами</xsl:when>
			<xsl:when test="$Code = '21.04'">Документы в сфере охраны окружающей среды и недропользования. Заключение о согласовании строительства и реконструкции объектов капитального строительства, внедрения новых технологических процессов и осуществления иной деятельности, оказывающей воздействие на водные биологические ресурсы и среду их обитания</xsl:when>
			<xsl:when test="$Code = '21.05'">Документы в сфере охраны окружающей среды и недропользования. Согласование проектной документации в отношении строительства и эксплуатации в пластах горных пород различных видов хранилищ углеводородного сырья и продуктов его переработки</xsl:when>
			<xsl:when test="$Code = '21.06'">Документы в сфере охраны окружающей среды и недропользования. Заключение об отсутствии полезных ископаемых в недрах под участком предстоящей застройки</xsl:when>
			<xsl:when test="$Code = '21.07'">Документы в сфере охраны окружающей среды и недропользования. Санитарно-эпидемиологическое заключение о соответствии санитарным правилам проекта зон санитарной охраны источника хозяйственно-питьевого водоснабжения</xsl:when>
			<xsl:when test="$Code = '21.08'">Документы в сфере охраны окружающей среды и недропользования. Документ о согласовании сооружения линий связи, электропередач, трубопроводов, дорог и других объектов на мелиорируемых (мелиорированных) землях</xsl:when>
			<xsl:when test="$Code = '21.09'">Документы в сфере охраны окружающей среды и недропользования. Документ об утверждении нормативов образования отходов производства и потребления и лимитов на их размещение</xsl:when>
			<xsl:when test="$Code = '21.10'">Документы в сфере охраны окружающей среды и недропользования. Согласование плана предупреждения и ликвидации разливов нефти и нефтепродуктов</xsl:when>
			<xsl:when test="$Code = '21.11'">Документы в сфере охраны окружающей среды и недропользования. Сведения о размерах водоохранных зон и прибрежных защитных полос, затрагиваемых в ходе строительства, поверхностных водных объектов</xsl:when>
			<xsl:when test="$Code = '21.12'">Документы в сфере охраны окружающей среды и недропользования. Сведения о наличии и месторасположении в районе размещения проектируемого объекта зон санитарной охраны источников водоснабжения (поверхностных и подземных)</xsl:when>
			<xsl:when test="$Code = '21.13'">Документы в сфере охраны окружающей среды и недропользования. Решение об установлении, изменении или о прекращении существования санитарно-защитной зоны</xsl:when>
			<xsl:when test="$Code = '21.99'">Документы в сфере охраны окружающей среды и недропользования. Иные документы</xsl:when>
			<xsl:when test="$Code = '22.01'">Документы в области организации транспортной инфраструктуры. Сведения о согласовании предварительной категории строящегося объекта транспортной инфраструктуры с компетентным органом в области обеспечения транспортной безопасности</xsl:when>
			<xsl:when test="$Code = '22.02'">Документы в области организации транспортной инфраструктуры. Согласование типов и конструкций устройств со специальными проходами, ограждающими опасные участки транспортных магистралей в местах концентрации объектов животного мира и на путях их миграции</xsl:when>
			<xsl:when test="$Code = '22.03'">Документы в области организации транспортной инфраструктуры. Решение о согласовании размещения объекта в границах полос воздушных подходов для аэродромов экспериментальной авиации, аэродромов государственной авиации, аэродромов гражданской авиации</xsl:when>
			<xsl:when test="$Code = '22.04'">Документы в области организации транспортной инфраструктуры. Решение об установлении приаэродромной территории</xsl:when>
			<xsl:when test="$Code = '22.05'">Документы в области организации транспортной инфраструктуры. Сведения о зонах с особыми условиями использования территорий объектов инфраструктуры метрополитена</xsl:when>
			<xsl:when test="$Code = '22.99'">Документы в области организации транспортной инфраструктуры. Иные документы</xsl:when>
			<xsl:when test="$Code = '23.01'">Документы в отношении объектов культурного наследия. Паспорт объекта культурного наследия</xsl:when>
			<xsl:when test="$Code = '23.02'">Документы в отношении объектов культурного наследия. Согласование проектных решений раздела по обеспечению сохранности объектов культурного наследия либо проектной документации по реставрации и приспособлению объекта культурного наследия</xsl:when>
			<xsl:when test="$Code = '23.99'">Документы в отношении объектов культурного наследия. Иные документы</xsl:when>
			<xsl:when test="$Code = '24.01'">Расчеты. Расчеты конструктивных, технологических и других решений, используемых в проектной документации</xsl:when>
			
			<xsl:when test="$Code = '25.01'">Состав сметной документации. Пояснительная записка к сметной документации</xsl:when>
			<xsl:when test="$Code = '25.02'">Состав сметной документации. Сводка затрат</xsl:when>
			<xsl:when test="$Code = '25.03'">Состав сметной документации. Сводный сметный расчет</xsl:when>
			<xsl:when test="$Code = '25.04'">Состав сметной документации. Объектный сметный расчет</xsl:when>
			<xsl:when test="$Code = '25.05'">Состав сметной документации. Локальный сметный расчет</xsl:when>
			<xsl:when test="$Code = '25.06'">Состав сметной документации. Сметные расчеты на отдельные виды затрат</xsl:when>
			
			<xsl:when test="$Code = '26.01'">Обоснование соответствия проектных значений параметров и других проектных характеристик здания или сооружения требованиям безопасности. Результаты исследований</xsl:when>
			<xsl:when test="$Code = '26.02'">Обоснование соответствия проектных значений параметров и других проектных характеристик здания или сооружения требованиям безопасности. Расчеты и (или) испытания, выполненные по сертифицированным или апробированным иным способом методикам</xsl:when>
			<xsl:when test="$Code = '26.03'">Обоснование соответствия проектных значений параметров и других проектных характеристик здания или сооружения требованиям безопасности. Моделирование сценариев возникновения опасных природных процессов и явлений и (или) техногенных воздействий, в том числе при неблагоприятном сочетании опасных природных процессов и явлений и (или) техногенных воздействий</xsl:when>
			<xsl:when test="$Code = '26.04'">Обоснование соответствия проектных значений параметров и других проектных характеристик здания или сооружения требованиям безопасности. Оценка риска возникновения опасных природных процессов и явлений и (или) техногенных воздействий</xsl:when>
			
			<xsl:when test="$Code = '99.01'">Группа дополнительных документов. Документ, подтверждающий передачу проектной документации и (или) результатов инженерных изысканий застройщику (техническому заказчику)</xsl:when>
			<xsl:when test="$Code = '99.02'">Группа дополнительных документов. Справка с описанием изменений, внесенных в проектную документацию и (или) результаты инженерных изысканий</xsl:when>
			<xsl:when test="$Code = '99.03'">Группа дополнительных документов. Акт (решение) собственника здания (строения, сооружения), содержащий условия реконструкции, капитального ремонта или сноса объекта капитального строительства или его части</xsl:when>
			<xsl:when test="$Code = '99.99'">Группа дополнительных документов. Иной документ</xsl:when>
		</xsl:choose>
	</xsl:template>
		
	<xsl:template name="TextBlockInTable">
		<xsl:param name="obj"/>
		<xsl:if test="$obj">
			<table>
				<tr><td>
					<xsl:for-each select="$obj">
						<xsl:if test="@Title">
							<h5><xsl:value-of select="@Title"/></h5>
						</xsl:if>
						<xsl:apply-templates select="."/>
					</xsl:for-each>
				</td></tr>
			</table>
		</xsl:if>
		<xsl:if test="not($obj)">
			<table>
				<tr><td>
					Требования отсутствуют
				</td></tr>
			</table>
		</xsl:if>
	</xsl:template>
	
	<xsl:template name="TextBlockNotInTable">
		<xsl:param name="obj"/>
		<xsl:if test="$obj">
			<xsl:for-each select="$obj">
				<xsl:if test="@Title">
					<h5><xsl:value-of select="@Title"/></h5>
				</xsl:if>
				<xsl:apply-templates select="."/>
			</xsl:for-each>
		</xsl:if>
	</xsl:template>
	
	<xsl:template match="Text">
		<xsl:call-template name="StringReplace">
			<xsl:with-param name="input" select="."/>
		</xsl:call-template>
	</xsl:template>
	
	<xsl:template match="SubTitle">
		<h5 class="left"><xsl:value-of select="."/></h5>
	</xsl:template>
		
	<xsl:template match="Image">
		<p align="center">
			<img>
				<xsl:attribute name="src">
					<xsl:value-of select="concat('data:image/', @Type, ';base64,', ImageData)"/>
				</xsl:attribute>
			</img>
			<xsl:if test="Comment">
				<xsl:value-of select="Comment"/>
			</xsl:if>
		</p>
		<br/>
	</xsl:template>
		
	<xsl:template match="Table">
		<table>
			<xsl:for-each select="Head|Body|Foot">
				<xsl:apply-templates select="."/>
			</xsl:for-each>
		</table>
	</xsl:template>
	
	<xsl:template match="Head">
		<thead>
			<xsl:for-each select="Row">
				<tr class="center">
					<xsl:if test="@Align!=''">
						<xsl:attribute name="align"><xsl:value-of select="@Align"/></xsl:attribute>	
					</xsl:if>
					<xsl:apply-templates select=".">
						<xsl:with-param name="type" select="'IsHead'"/>
					</xsl:apply-templates>
				</tr>
			</xsl:for-each>
		</thead>
	</xsl:template>
		
	<xsl:template match="Body">
		<tbody>
			<xsl:for-each select="Row">
				<tr>
					<xsl:if test="@Align!=''">
						<xsl:attribute name="align"><xsl:value-of select="@Align"/></xsl:attribute>	
					</xsl:if>
					<xsl:apply-templates select="."/>
				</tr>
			</xsl:for-each>
		</tbody>
	</xsl:template>
		
	<xsl:template match="Foot">
		<tfoot>
			<xsl:for-each select="Row">
				<tr>
					<xsl:if test="@Align!=''">
						<xsl:attribute name="align"><xsl:value-of select="@Align"/></xsl:attribute>	
					</xsl:if>
					<xsl:apply-templates select="."/>
				</tr>
			</xsl:for-each>
		</tfoot>
	</xsl:template>
	
	<xsl:template match="Cell">
		<xsl:param name="type" select="''"/>
		
		<xsl:choose>
			<xsl:when test="$type='IsHead'">
				<th>
					<xsl:if test="@Colspan!=''">
						<xsl:attribute name="colspan"><xsl:value-of select="@Colspan"/></xsl:attribute>	
					</xsl:if>
					<xsl:if test="@Rowspan!=''">
						<xsl:attribute name="rowspan"><xsl:value-of select="@Rowspan"/></xsl:attribute>	
					</xsl:if>
					<xsl:if test="@Align!=''">
						<xsl:attribute name="align"><xsl:value-of select="@Align"/></xsl:attribute>	
					</xsl:if>
					
					<xsl:call-template name="StringReplace">
						<xsl:with-param name="input" select="."/>
					</xsl:call-template>
					
				</th>
			</xsl:when>
			<xsl:otherwise>
				<td>
					<xsl:if test="@Colspan!=''">
						<xsl:attribute name="colspan"><xsl:value-of select="@Colspan"/></xsl:attribute>	
					</xsl:if>
					<xsl:if test="@Rowspan!=''">
						<xsl:attribute name="rowspan"><xsl:value-of select="@Rowspan"/></xsl:attribute>	
					</xsl:if>
					<xsl:if test="@Align!=''">
						<xsl:attribute name="align"><xsl:value-of select="@Align"/></xsl:attribute>	
					</xsl:if>
					<xsl:call-template name="StringReplace">
						<xsl:with-param name="input" select="."/>
					</xsl:call-template>
					
				</td>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template match="Date">
		<xsl:if test=". != ''">
			<xsl:variable name="mm">
				<xsl:value-of select="substring(., 9, 2)"/>
			</xsl:variable>
			<xsl:variable name="dd">
				<xsl:value-of select="substring(., 6, 2)"/>
			</xsl:variable>
			<xsl:variable name="yyyy">
				<xsl:value-of select="substring(., 1, 4)"/>
			</xsl:variable>
			<xsl:value-of select="concat($mm, '.', $dd, '.', $yyyy)"/>
		</xsl:if>
	</xsl:template>
		
	<xsl:template name="FormatDate">
		<xsl:param name="DateTimeStr"/>
		<xsl:if test="$DateTimeStr != ''">
			<xsl:variable name="mm">
				<xsl:value-of select="substring($DateTimeStr, 9, 2)"/>
			</xsl:variable>
			<xsl:variable name="dd">
				<xsl:value-of select="substring($DateTimeStr, 6, 2)"/>
			</xsl:variable>
			<xsl:variable name="yyyy">
				<xsl:value-of select="substring($DateTimeStr, 1, 4)"/>
			</xsl:variable>
			<xsl:value-of select="concat($mm, '.', $dd, '.', $yyyy)"/>
		</xsl:if>
	</xsl:template>

	<xsl:template name="StringReplace">
		<xsl:param name="input"/>
		<xsl:choose>
			<xsl:when test="contains($input, '&#xA;')">
				<p>
					<xsl:value-of select="substring-before($input, '&#xA;')"/>
				</p>
				<xsl:call-template name="StringReplace">
					<xsl:with-param name="input" select="substring-after($input, '&#xA;')"/>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<p><xsl:value-of select="$input"/></p>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="StringReplaceComment">
		<xsl:param name="input"/>
		<xsl:param name="count"/>
		<xsl:param name="first"/>
		<xsl:choose>
			<xsl:when test="contains($input, '&#xA;')">
				<p>
					<xsl:if test="$first=1">
						<sup>
							<xsl:call-template name="FootNoteSymbols">
								<xsl:with-param name="Count" select="$count"/>
							</xsl:call-template>
						</sup>
						<xsl:text> </xsl:text>
					</xsl:if>
					<xsl:value-of select="substring-before($input, '&#xA;')"/>
				</p>
				<xsl:call-template name="StringReplaceComment">
					<xsl:with-param name="input" select="substring-after($input, '&#xA;')"/>
					<xsl:with-param name="count" select="0"/>
					<xsl:with-param name="first" select="number($first)+1"/>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<p>
					<xsl:if test="$first=1">
						<sup>
							<xsl:call-template name="FootNoteSymbols">
								<xsl:with-param name="Count" select="$count"/>
							</xsl:call-template>
						</sup>
						<xsl:text> </xsl:text>
					</xsl:if>
					<xsl:value-of select="$input"/>
				</p>
				<xsl:if test="$count &gt; 1">
					<br/>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="FootNoteSymbols">
		<xsl:param name="Count"/>
		<xsl:if test="$Count!=0">
			<xsl:text>*</xsl:text>
			<xsl:if test="$Count != 1">
				<xsl:call-template name="FootNoteSymbols">
					<xsl:with-param name="Count" select="number($Count) - 1"/>
				</xsl:call-template>
			</xsl:if>
		</xsl:if>
	</xsl:template>

	<xsl:template match="Organization">
		<xsl:param name="ShowType" select="0"/>
		<xsl:param name="ShowSRO" select="0"/>
		
		<table>
			<xsl:if test="$ShowType!=0">
				<thead>
					<tr><td colspan="2" class="left"><b>
						<xsl:if test="current()[RAFP]">Представительство (филиал) иностранного юридического лица:</xsl:if>
						<xsl:if test="current()[OGRN]">Юридическое лицо:</xsl:if>
						</b>
					</td></tr>
				</thead>
			</xsl:if>
			<tbody>
				<tr><td style="width:25%">Полное наименование:</td><td><xsl:value-of select="FullName"/></td></tr>
				<xsl:if test="AbbreviatedName">
					<tr><td>Сокращенное наименование:</td><td><xsl:value-of select="AbbreviatedName"/></td></tr>
				</xsl:if>
				<xsl:if test="OGRN">
					<tr><td title="Основной государственный регистрационный номер">ОГРН:</td><td><xsl:value-of select="OGRN"/></td></tr>	
				</xsl:if>
				<xsl:if test="RAFP">
					<tr><td title = "Номер записи об аккредитации в государственном реестре аккредитованных филиалов, представительств иностранных юридических лиц">Номер записи об аккредитации в РАФП:</td><td><xsl:value-of select="RAFP"/></td></tr>	
				</xsl:if>
				<tr><td title="Идентификационный номер налогоплательщика">ИНН:</td><td><xsl:value-of select="INN"/></td></tr>
				<tr><td title="Код причины постановки на учет">КПП:</td><td><xsl:value-of select="KPP"/></td></tr>
				<tr><td>Адрес:</td><td><xsl:apply-templates select="Address"/></td></tr>
				<xsl:if test="Email">
					<tr><td>Адрес электронной почты:</td><td><xsl:value-of select="Email"/></td></tr>
				</xsl:if>
				<xsl:if test="$ShowSRO!=0">
					<xsl:apply-templates select="../SROMembership"/>
				</xsl:if>
			</tbody>
		</table>
	</xsl:template>

	<xsl:template match="IndividualEntrepreneur">
		<xsl:param name="ShowType" select="0"/>
		<xsl:param name="ShowSRO" select="0"/>
		<table>
			<xsl:if test="$ShowType!=0">
				<thead>
					<tr><td colspan="2" class="left"><b>Индивидуальный предприниматель:</b></td></tr>
				</thead>
			</xsl:if>
			<tbody>
				<tr><td style="width:25%">Фамилия:</td><td><xsl:value-of select="Surname"/></td></tr>
				<tr><td>Имя:</td><td><xsl:value-of select="Name"/></td></tr>
				<xsl:if test="Patronymic">
					<tr><td>Отчество:</td><td><xsl:value-of select="Patronymic"/></td></tr>	
				</xsl:if>
				<xsl:if test="OGRNIP">
					<tr><td title="Основной государственный регистрационный номер индивидуального предпринимателя">ОГРНИП:</td><td><xsl:value-of select="OGRNIP"/></td></tr>	
				</xsl:if>
				<xsl:if test="INN">
					<tr><td title="Идентификационный номер налогоплательщика">ИНН:</td><td><xsl:value-of select="INN"/></td></tr>
				</xsl:if>
				<tr><td>Почтовый адрес:</td><td><xsl:apply-templates select="PostAddress"/></td></tr>
				<xsl:if test="Email">
					<tr><td>Адрес электронной почты:</td><td><xsl:value-of select="Email"/></td></tr>
				</xsl:if>
				<xsl:if test="$ShowSRO!=0">
					<xsl:apply-templates select="../SROMembership"/>
				</xsl:if>
			</tbody>
		</table>
	</xsl:template>
		
	<xsl:template match="Person">
		<xsl:param name="ShowType" select="0"/>
		<table>
			<xsl:if test="$ShowType!=0">
				<thead>
					<tr><td colspan="2" class="left"><b>Физическое лицо:</b></td></tr>
				</thead>
			</xsl:if>
			<tbody>
				<tr><td style="width:25%">Фамилия:</td><td><xsl:value-of select="Surname"/></td></tr>
				<tr><td>Имя:</td><td><xsl:value-of select="Name"/></td></tr>
				<xsl:if test="Patronymic">
					<tr><td>Отчество:</td><td><xsl:value-of select="Patronymic"/></td></tr>	
				</xsl:if>
				<!--
				<xsl:if test="SNILS">
					<tr><td title="Страховой номер индивидуального лицевого счёта">СНИЛС:</td><td><xsl:value-of select="SNILS"/></td></tr>
				</xsl:if>
				-->
				<tr><td>Почтовый адрес:</td><td><xsl:apply-templates select="PostAddress"/></td></tr>
				<xsl:if test="Email">
					<tr><td>Адрес электронной почты:</td><td><xsl:value-of select="Email"/></td></tr>
				</xsl:if>
			</tbody>
		</table>
	</xsl:template>
	
	<xsl:template match="Address|PostAddress|Crossing|BeginAddress|FinalAddress">
		<xsl:if test="position() != 1">; </xsl:if>
		<xsl:if test="PostIndex">
			<xsl:if test="PostIndex">
				<xsl:value-of select="PostIndex"/>, </xsl:if>
		</xsl:if>
		<xsl:if test="Country">
			<xsl:value-of select="Country"/>
			<xsl:if test="RegionCode != '00' or District or City or Settlement or Street or Building or Room or Note">, </xsl:if>
		</xsl:if>
		<xsl:if test="RegionCode != '00'">
			<xsl:apply-templates select="RegionCode"/>
			<xsl:if test="District or City or Settlement or Street or Building or Room or Note">,
			</xsl:if>
		</xsl:if>
		<xsl:if test="District">
			<xsl:value-of select="District"/>
			<xsl:if test="City or Settlement or Street or Building or Room or Note">, </xsl:if>
		</xsl:if>
		<xsl:if test="City">
			<xsl:value-of select="City"/>
			<xsl:if test="Settlement or Street or Building or Room or Note">, </xsl:if>
		</xsl:if>
		<xsl:if test="Settlement">
			<xsl:value-of select="Settlement"/>
			<xsl:if test="Street or Building or Room or Note">, </xsl:if>
		</xsl:if>
		<xsl:if test="Street">
			<xsl:value-of select="Street"/>
			<xsl:if test="Building or Room or Note">, </xsl:if>
		</xsl:if>
		<xsl:if test="Building">
			<xsl:value-of select="Building"/>
			<xsl:if test="Room or Note">, </xsl:if>
		</xsl:if>
		<xsl:if test="Room">
			<xsl:value-of select="Room"/>
			<xsl:if test="Note">, </xsl:if>
		</xsl:if>
		<xsl:if test="Note">
			<xsl:value-of select="Note"/>
		</xsl:if>
	</xsl:template>

	<xsl:template name="FunctionalRolesList">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code = 1">УТВЕРЖДЕНО</xsl:when>
			<xsl:when test="$Code = 2">СОГЛАСОВАНО</xsl:when>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="RegionCode">
		<xsl:choose>
			<xsl:when test=". = 00">Объект расположен за пределами территории Российской Федерации, во внутренних морских водах, территориальном море и прилежащей зоне Российской Федерации, в исключительной экономической зоне Российской Федерации, в границах российской части (российском секторе) дна Каспийского моря и континентального шельфа Российской Федерации</xsl:when>
			<xsl:when test=". = 1">Республика Адыгея (Адыгея)</xsl:when>
			<xsl:when test=". = 2">Республика Башкортостан</xsl:when>
			<xsl:when test=". = 3">Республика Бурятия</xsl:when>
			<xsl:when test=". = 4">Республика Алтай</xsl:when>
			<xsl:when test=". = 5">Республика Дагестан</xsl:when>
			<xsl:when test=". = 6">Республика Ингушетия</xsl:when>
			<xsl:when test=". = 7">Кабардино-Балкарская Республика</xsl:when>
			<xsl:when test=". = 8">Республика Калмыкия</xsl:when>
			<xsl:when test=". = 9">Карачаево-Черкесская Республика</xsl:when>
			<xsl:when test=". = 10">Республика Карелия</xsl:when>
			<xsl:when test=". = 11">Республика Коми</xsl:when>
			<xsl:when test=". = 12">Республика Марий Эл</xsl:when>
			<xsl:when test=". = 13">Республика Мордовия</xsl:when>
			<xsl:when test=". = 14">Республика Саха (Якутия)</xsl:when>
			<xsl:when test=". = 15">Республика Северная Осетия-Алания</xsl:when>
			<xsl:when test=". = 16">Республика Татарстан (Татарстан)</xsl:when>
			<xsl:when test=". = 17">Республика Тыва</xsl:when>
			<xsl:when test=". = 18">Удмуртская Республика</xsl:when>
			<xsl:when test=". = 19">Республика Хакасия</xsl:when>
			<xsl:when test=". = 20">Чеченская Республика</xsl:when>
			<xsl:when test=". = 21">Чувашская Республика-Чувашия</xsl:when>
			<xsl:when test=". = 22">Алтайский край</xsl:when>
			<xsl:when test=". = 23">Краснодарский край</xsl:when>
			<xsl:when test=". = 24">Красноярский край</xsl:when>
			<xsl:when test=". = 25">Приморский край</xsl:when>
			<xsl:when test=". = 26">Ставропольский край</xsl:when>
			<xsl:when test=". = 27">Хабаровский край</xsl:when>
			<xsl:when test=". = 28">Амурская область</xsl:when>
			<xsl:when test=". = 29">Архангельская область</xsl:when>
			<xsl:when test=". = 30">Астраханская область</xsl:when>
			<xsl:when test=". = 31">Белгородская область</xsl:when>
			<xsl:when test=". = 32">Брянская область</xsl:when>
			<xsl:when test=". = 33">Владимирская область</xsl:when>
			<xsl:when test=". = 34">Волгоградская область</xsl:when>
			<xsl:when test=". = 35">Вологодская область</xsl:when>
			<xsl:when test=". = 36">Воронежская область</xsl:when>
			<xsl:when test=". = 37">Ивановская область</xsl:when>
			<xsl:when test=". = 38">Иркутская область</xsl:when>
			<xsl:when test=". = 39">Калининградская область</xsl:when>
			<xsl:when test=". = 40">Калужская область</xsl:when>
			<xsl:when test=". = 41">Камчатский край</xsl:when>
			<xsl:when test=". = 42">Кемеровская область - Кузбасс</xsl:when>
			<xsl:when test=". = 43">Кировская область</xsl:when>
			<xsl:when test=". = 44">Костромская область</xsl:when>
			<xsl:when test=". = 45">Курганская область</xsl:when>
			<xsl:when test=". = 46">Курская область</xsl:when>
			<xsl:when test=". = 47">Ленинградская область</xsl:when>
			<xsl:when test=". = 48">Липецкая область</xsl:when>
			<xsl:when test=". = 49">Магаданская область</xsl:when>
			<xsl:when test=". = 50">Московская область</xsl:when>
			<xsl:when test=". = 51">Мурманская область</xsl:when>
			<xsl:when test=". = 52">Нижегородская область</xsl:when>
			<xsl:when test=". = 53">Новгородская область</xsl:when>
			<xsl:when test=". = 54">Новосибирская область</xsl:when>
			<xsl:when test=". = 55">Омская область</xsl:when>
			<xsl:when test=". = 56">Оренбургская область</xsl:when>
			<xsl:when test=". = 57">Орловская область</xsl:when>
			<xsl:when test=". = 58">Пензенская область</xsl:when>
			<xsl:when test=". = 59">Пермский край</xsl:when>
			<xsl:when test=". = 60">Псковская область</xsl:when>
			<xsl:when test=". = 61">Ростовская область</xsl:when>
			<xsl:when test=". = 62">Рязанская область</xsl:when>
			<xsl:when test=". = 63">Самарская область</xsl:when>
			<xsl:when test=". = 64">Саратовская область</xsl:when>
			<xsl:when test=". = 65">Сахалинская область</xsl:when>
			<xsl:when test=". = 66">Свердловская область</xsl:when>
			<xsl:when test=". = 67">Смоленская область</xsl:when>
			<xsl:when test=". = 68">Тамбовская область</xsl:when>
			<xsl:when test=". = 69">Тверская область</xsl:when>
			<xsl:when test=". = 70">Томская область</xsl:when>
			<xsl:when test=". = 71">Тульская область</xsl:when>
			<xsl:when test=". = 72">Тюменская область</xsl:when>
			<xsl:when test=". = 73">Ульяновская область</xsl:when>
			<xsl:when test=". = 74">Челябинская область</xsl:when>
			<xsl:when test=". = 75">Забайкальский край</xsl:when>
			<xsl:when test=". = 76">Ярославская область</xsl:when>
			<xsl:when test=". = 77">Москва</xsl:when>
			<xsl:when test=". = 78">Санкт-Петербург</xsl:when>
			<xsl:when test=". = 79">Еврейская автономная область</xsl:when>
			<xsl:when test=". = 80">Донецкая Народная Республика</xsl:when>
			<xsl:when test=". = 81">Луганская Народная Республика</xsl:when>
			<xsl:when test=". = 83">Ненецкий автономный округ</xsl:when>
			<xsl:when test=". = 84">Херсонская область</xsl:when>
			<xsl:when test=". = 85">Запорожская область</xsl:when>
			<xsl:when test=". = 86">Ханты-Мансийский автономный округ - Югра</xsl:when>
			<xsl:when test=". = 87">Чукотский автономный округ</xsl:when>
			<xsl:when test=". = 89">Ямало-Ненецкий автономный округ</xsl:when>
			<xsl:when test=". = 91">Республика Крым</xsl:when>
			<xsl:when test=". = 92">Севастополь</xsl:when>
		</xsl:choose>
	</xsl:template>
		
	<xsl:template match="ConstructionType">
		<xsl:choose>
			<xsl:when test=". = 1">Строительство</xsl:when>
			<xsl:when test=". = 2">Реконструкция</xsl:when>
			<xsl:when test=". = 3">Капитальный ремонт</xsl:when>
			<xsl:when test=". = 4">Снос объекта капитального строительства</xsl:when>
			<xsl:when test=". = 5">Сохранение объекта культурного наследия</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template match="Level">
		<xsl:choose>
			<xsl:when test=". = 1">Федеральный бюджет</xsl:when>
			<xsl:when test=". = 2">Бюджет субъекта Российской Федерации</xsl:when>
			<xsl:when test=". = 3">Местный бюджет</xsl:when>
			<xsl:when test=". = 4">Бюджет территориального государственного внебюджетного фонда</xsl:when>
			<xsl:when test=". = 5">Бюджет государственного внебюджетного фонда Российской Федерации</xsl:when>
		</xsl:choose>
	</xsl:template>
		
	<xsl:template name="RequirementsList">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code = 1">Наличие СРО - ИИ</xsl:when>
			<xsl:when test="$Code = 2">Наличие СРО - ПД</xsl:when>
			<xsl:when test="$Code = 3">Наличие сертификата соответствия требованиям ГОСТ Р ИСО 9001-2015</xsl:when>
			<xsl:when test="$Code = 4">Наличие сертификата соответствия требованиям ГОСТ Р ИСО 14001-2016</xsl:when>
			<xsl:when test="$Code = 5">Наличие лицензии на осуществление работ, связанных с использованием сведений, составляющих государственную тайну</xsl:when>
			<xsl:when test="$Code = 6">Согласование с Департаментом безопасности ПАО «Транснефть» субподрядных проектных организаций, определённых для проектирования ИТСО</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template match="ObjectType">
		<xsl:choose>
			<xsl:when test=". = 1">Объект производственного назначения</xsl:when>
			<xsl:when test=". = 2">Объект непроизводственного назначения</xsl:when>
			<xsl:when test=". = 3">Линейный объект</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template name="ResponsibilityLeveldList">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code = 1">Повышенный</xsl:when>
			<xsl:when test="$Code = 2">Нормальный</xsl:when>
			<xsl:when test="$Code = 3">Пониженный</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template match="SecurityLabel">
		<xsl:choose>
			<xsl:when test=". = 0">Без грифа</xsl:when>
			<xsl:when test=". = 1">Конфиденциально</xsl:when>
			<xsl:when test=". = 2">Коммерческая тайна</xsl:when>
			<xsl:when test=". = 3">Данный материал запрещается размножать, передавать другим организациям и лицам для целей, не предусмотренных настоящим документом</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template name="LandCategoryList">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code = 1">Земли сельскохозяйственного назначения</xsl:when>
			<xsl:when test="$Code = 2">Земли населенных пунктов</xsl:when>
			<xsl:when test="$Code = 3">Земли промышленности, энергетики, транспорта, связи, радиовещания, телевидения, информатики, земли для обеспечения космической деятельности, земли обороны, безопасности и земли иного специального назначения</xsl:when>
			<xsl:when test="$Code = 4">Земли особо охраняемых территорий и объектов</xsl:when>
			<xsl:when test="$Code = 5">Земли лесного фонда</xsl:when>
			<xsl:when test="$Code = 6">Земли водного фонда</xsl:when>
			<xsl:when test="$Code = 7">Земли запаса</xsl:when>
		</xsl:choose>
	</xsl:template>
		
	<xsl:template name="StagesList">
		<xsl:param name="Code"/>
		<xsl:choose>
			<xsl:when test="$Code = 1">Проектная документация</xsl:when>
			<xsl:when test="$Code = 2">Рабочая документация</xsl:when>
		</xsl:choose>
	</xsl:template>
		
	<xsl:template match="Measure|@Measure">
        <xsl:choose>
        	<xsl:when test=". = '-'">-</xsl:when><!--Миллиметр-->
        	<xsl:when test=". = '003'">мм</xsl:when><!--Миллиметр-->
			<xsl:when test=". = '004'">см</xsl:when><!--Сантиметр-->
			<xsl:when test=". = '005'">дм</xsl:when><!--Дециметр-->
			<xsl:when test=". = '006'">м</xsl:when><!--Метр-->
			<xsl:when test=". = '008'">км; тыс. м</xsl:when><!--Километр; тысяча метров-->
			<xsl:when test=". = '009'">Мм; млн. м</xsl:when><!--Мегаметр; миллион метров-->
			<xsl:when test=". = '039'">дюйм</xsl:when><!--Дюйм (25,4 мм)-->
			<xsl:when test=". = '041'">фут</xsl:when><!--Фут (0,3048 м)-->
			<xsl:when test=". = '043'">ярд</xsl:when><!--Ярд (0,9144 м)-->
			<xsl:when test=". = '047'">миля</xsl:when><!--Морская миля (1852 м)-->
			<xsl:when test=". = '050'">мм<sup><small>2</small></sup></xsl:when><!--Квадратный миллиметр-->
			<xsl:when test=". = '051'">см<sup><small>2</small></sup></xsl:when><!--Квадратный сантиметр-->
			<xsl:when test=". = '053'">дм<sup><small>2</small></sup></xsl:when><!--Квадратный дециметр-->
			<xsl:when test=". = '055'">м<sup><small>2</small></sup></xsl:when><!--Квадратный метр-->
			<xsl:when test=". = '058'">тыс. м<sup><small>2</small></sup></xsl:when><!--Тысяча квадратных метров-->
			<xsl:when test=". = '059'">га</xsl:when><!--Гектар-->
			<xsl:when test=". = '061'">км<sup><small>2</small></sup></xsl:when><!--Квадратный километр-->
			<xsl:when test=". = '071'">дюйм<sup><small>2</small></sup></xsl:when><!--Квадратный дюйм (645,16 мм<sup><small>2)-->
			<xsl:when test=". = '073'">фут<sup><small>2</small></sup></xsl:when><!--Квадратный фут (0,092903 м<sup><small>2)-->
			<xsl:when test=". = '075'">ярд<sup><small>2</small></sup></xsl:when><!--Квадратный ярд (0,8361274 м<sup><small>2)-->
			<xsl:when test=". = '109'">а</xsl:when><!--Ар (100 м<sup><small>2)-->
			<xsl:when test=". = '110'">мм<sup><small>3</small></sup></xsl:when><!--Кубический миллиметр-->
			<xsl:when test=". = '111'">см<sup><small>3</small></sup>; мл</xsl:when><!--Кубический сантиметр; миллилитр-->
			<xsl:when test=". = '112'">л; дм<sup><small>3</small></sup></xsl:when><!--Литр; кубический дециметр-->
			<xsl:when test=". = '113'">м<sup><small>3</small></sup></xsl:when><!--Кубический метр-->
			<xsl:when test=". = '118'">дл</xsl:when><!--Децилитр-->
			<xsl:when test=". = '122'">гл</xsl:when><!--Гектолитр-->
			<xsl:when test=". = '126'">Мл</xsl:when><!--Мегалитр-->
			<xsl:when test=". = '131'">дюйм<sup><small>3</small></sup></xsl:when><!--Кубический дюйм (16387,1 мм<sup><small>3)-->
			<xsl:when test=". = '132'">фут<sup><small>3</small></sup></xsl:when><!--Кубический фут (0,02831685 м<sup><small>3)-->
			<xsl:when test=". = '133'">ярд<sup><small>3</small></sup></xsl:when><!--Кубический ярд (0,764555 м<sup><small>3)-->
			<xsl:when test=". = '159'">млн. м<sup><small>3</small></sup></xsl:when><!--Миллион кубических метров-->
			<xsl:when test=". = '160'">гг</xsl:when><!--Гектограмм-->
			<xsl:when test=". = '161'">мг</xsl:when><!--Миллиграмм-->
			<xsl:when test=". = '162'">кар</xsl:when><!--Метрический карат-->
			<xsl:when test=". = '163'">г</xsl:when><!--Грамм-->
			<xsl:when test=". = '166'">кг</xsl:when><!--Килограмм-->
			<xsl:when test=". = '168'">т</xsl:when><!--Тонна; метрическая тонна (1000 кг)-->
			<xsl:when test=". = '170'">тыс. т</xsl:when><!--Килотонна-->
			<xsl:when test=". = '173'">сг</xsl:when><!--Сантиграмм-->
			<xsl:when test=". = '181'">БРТ</xsl:when><!--Брутто-регистровая тонна (2,8316 м<sup><small>3)-->
			<xsl:when test=". = '185'">т грп</xsl:when><!--Грузоподъемность в метрических тоннах-->
			<xsl:when test=". = '206'">ц</xsl:when><!--Центнер (метрический) (100 кг); гектокилограмм; квинтал (метрический); децитонна-->
			<xsl:when test=". = '212'">Вт</xsl:when><!--Ватт-->
			<xsl:when test=". = '214'">кВт</xsl:when><!--Киловатт-->
			<xsl:when test=". = '215'">МВт; тыс. кВт</xsl:when><!--Мегаватт; тысяча киловатт-->
			<xsl:when test=". = '222'">В</xsl:when><!--Вольт-->
			<xsl:when test=". = '223'">кВ</xsl:when><!--Киловольт-->
			<xsl:when test=". = '227'">кВ.А</xsl:when><!--Киловольт-ампер-->
			<xsl:when test=". = '228'">МВ.А</xsl:when><!--Мегавольт-ампер (тысяча киловольт-ампер)-->
			<xsl:when test=". = '230'">квар</xsl:when><!--Киловар-->
			<xsl:when test=". = '243'">Вт.ч</xsl:when><!--Ватт-час-->
			<xsl:when test=". = '245'">кВт.ч</xsl:when><!--Киловатт-час-->
			<xsl:when test=". = '246'">МВт.ч; тыс. кВт.ч</xsl:when><!--Мегаватт-час; 1000 киловатт-часов-->
			<xsl:when test=". = '247'">ГВт.ч</xsl:when><!--Гигаватт-час (миллион киловатт-часов)-->
			<xsl:when test=". = '260'">А</xsl:when><!--Ампер-->
			<xsl:when test=". = '263'">А.ч</xsl:when><!--Ампер-час (3,6 кКл)-->
			<xsl:when test=". = '264'">тыс. А.ч</xsl:when><!--Тысяча ампер-часов-->
			<xsl:when test=". = '270'">Кл</xsl:when><!--Кулон-->
			<xsl:when test=". = '271'">Дж</xsl:when><!--Джоуль-->
			<xsl:when test=". = '273'">кДж</xsl:when><!--Килоджоуль-->
			<xsl:when test=". = '274'">Ом</xsl:when><!--Ом-->
			<xsl:when test=". = '280'">°C</xsl:when><!--Градус Цельсия-->
			<xsl:when test=". = '281'">°F</xsl:when><!--Градус Фаренгейта-->
			<xsl:when test=". = '282'">кд</xsl:when><!--Кандела-->
			<xsl:when test=". = '283'">лк</xsl:when><!--Люкс-->
			<xsl:when test=". = '284'">лм</xsl:when><!--Люмен-->
			<xsl:when test=". = '288'">K</xsl:when><!--Кельвин-->
			<xsl:when test=". = '289'">Н</xsl:when><!--Ньютон-->
			<xsl:when test=". = '290'">Гц</xsl:when><!--Герц-->
			<xsl:when test=". = '291'">кГц</xsl:when><!--Килогерц-->
			<xsl:when test=". = '292'">МГц</xsl:when><!--Мегагерц-->
			<xsl:when test=". = '294'">Па</xsl:when><!--Паскаль-->
			<xsl:when test=". = '296'">См</xsl:when><!--Сименс-->
			<xsl:when test=". = '297'">кПа</xsl:when><!--Килопаскаль-->
			<xsl:when test=". = '298'">МПа</xsl:when><!--Мегапаскаль-->
			<xsl:when test=". = '300'">атм</xsl:when><!--Физическая атмосфера (101325 Па)-->
			<xsl:when test=". = '301'">ат</xsl:when><!--Техническая атмосфера (98066,5 Па)-->
			<xsl:when test=". = '302'">ГБк</xsl:when><!--Гигабеккерель-->
			<xsl:when test=". = '304'">мКи</xsl:when><!--Милликюри-->
			<xsl:when test=". = '305'">Ки</xsl:when><!--Кюри-->
			<xsl:when test=". = '306'">г Д/И</xsl:when><!--Грамм делящихся изотопов-->
			<xsl:when test=". = '308'">мб</xsl:when><!--Миллибар-->
			<xsl:when test=". = '309'">бар</xsl:when><!--Бар-->
			<xsl:when test=". = '310'">гб</xsl:when><!--Гектобар-->
			<xsl:when test=". = '312'">кб</xsl:when><!--Килобар-->
			<xsl:when test=". = '314'">Ф</xsl:when><!--Фарад-->
			<xsl:when test=". = '316'">кг/м<sup><small>3</small></sup></xsl:when><!--Килограмм на кубический метр-->
			<xsl:when test=". = '323'">Бк</xsl:when><!--Беккерель-->
			<xsl:when test=". = '324'">Вб</xsl:when><!--Вебер-->
			<xsl:when test=". = '327'">уз</xsl:when><!--Узел (миля/ч)-->
			<xsl:when test=". = '328'">м/с</xsl:when><!--Метр в секунду-->
			<xsl:when test=". = '330'">об/с</xsl:when><!--Оборот в секунду-->
			<xsl:when test=". = '331'">об/мин</xsl:when><!--Оборот в минуту-->
			<xsl:when test=". = '333'">км/ч</xsl:when><!--Километр в час-->
			<xsl:when test=". = '335'">м/с<sup><small>2</small></sup></xsl:when><!--Метр на секунду в квадрате-->
			<xsl:when test=". = '349'">Кл/кг</xsl:when><!--Кулон на килограмм-->
			<xsl:when test=". = '354'">с</xsl:when><!--Секунда-->
			<xsl:when test=". = '355'">мин</xsl:when><!--Минута-->
			<xsl:when test=". = '356'">ч</xsl:when><!--Час-->
			<xsl:when test=". = '359'">сут; дн</xsl:when><!--Сутки-->
			<xsl:when test=". = '360'">нед</xsl:when><!--Неделя-->
			<xsl:when test=". = '361'">дек</xsl:when><!--Декада-->
			<xsl:when test=". = '362'">мес</xsl:when><!--Месяц-->
			<xsl:when test=". = '364'">кварт</xsl:when><!--Квартал-->
			<xsl:when test=". = '365'">полгода</xsl:when><!--Полугодие-->
			<xsl:when test=". = '366'">г; лет</xsl:when><!--Год-->
			<xsl:when test=". = '368'">деслет</xsl:when><!--Десятилетие-->
			<xsl:when test=". = '499'">кг/с</xsl:when><!--Килограмм в секунду-->
			<xsl:when test=". = '533'">т пар/ч</xsl:when><!--Тонна пара в час-->
			<xsl:when test=". = '596'">м<sup><small>3</small></sup>/с</xsl:when><!--Кубический метр в секунду-->
			<xsl:when test=". = '598'">м<sup><small>3</small></sup>/ч</xsl:when><!--Кубический метр в час-->
			<xsl:when test=". = '599'">тыс. м<sup><small>3</small></sup>/сут</xsl:when><!--Тысяча кубических метров в сутки-->
			<xsl:when test=". = '616'">боб</xsl:when><!--Бобина-->
			<xsl:when test=". = '625'">л.</xsl:when><!--Лист-->
			<xsl:when test=". = '626'">100 л.</xsl:when><!--Сто листов-->
			<xsl:when test=". = '630'">тыс станд. усл. кирп</xsl:when><!--Тысяча стандартных условных кирпичей-->
			<xsl:when test=". = '641'">дюжина</xsl:when><!--Дюжина (12 шт.)-->
			<xsl:when test=". = '657'">изд</xsl:when><!--Изделие-->
			<xsl:when test=". = '683'">100 ящ.</xsl:when><!--Сто ящиков-->
			<xsl:when test=". = '704'">набор</xsl:when><!--Набор-->
			<xsl:when test=". = '715'">пар</xsl:when><!--Пара (2 шт.)-->
			<xsl:when test=". = '730'">20</xsl:when><!--Два десятка-->
			<xsl:when test=". = '732'">10 пар</xsl:when><!--Десять пар-->
			<xsl:when test=". = '733'">дюжина пар</xsl:when><!--Дюжина пар-->
			<xsl:when test=". = '734'">посыл</xsl:when><!--Посылка-->
			<xsl:when test=". = '735'">часть</xsl:when><!--Часть-->
			<xsl:when test=". = '736'">рул</xsl:when><!--Рулон-->
			<xsl:when test=". = '737'">дюжина рул</xsl:when><!--Дюжина рулонов-->
			<xsl:when test=". = '740'">дюжина шт</xsl:when><!--Дюжина штук-->
			<xsl:when test=". = '745'">элем</xsl:when><!--Элемент-->
			<xsl:when test=". = '778'">упак</xsl:when><!--Упаковка-->
			<xsl:when test=". = '780'">дюжина упак</xsl:when><!--Дюжина упаковок-->
			<xsl:when test=". = '781'">100 упак</xsl:when><!--Сто упаковок-->
			<xsl:when test=". = '796'">шт</xsl:when><!--Штука-->
			<xsl:when test=". = '797'">100 шт</xsl:when><!--Сто штук-->
			<xsl:when test=". = '798'">тыс. шт; 1000 шт</xsl:when><!--Тысяча штук-->
			<xsl:when test=". = '799'">млн. шт</xsl:when><!--Миллион штук-->
			<xsl:when test=". = '800'">млрд. шт</xsl:when><!--Миллиард штук-->
			<xsl:when test=". = '801'">Биллион шт</xsl:when><!--Биллион штук (Европа); триллион штук-->
            <xsl:when test=". = '802'">Квинтильон шт</xsl:when><!--Квинтильон штук (Европа)-->
			<xsl:when test=". = '820'">креп. спирта по массе</xsl:when><!--Крепость спирта по массе-->
			<xsl:when test=". = '821'">креп. спирта по объему</xsl:when><!--Крепость спирта по объему-->
			<xsl:when test=". = '831'">л 100% спирта</xsl:when><!--Литр чистого (100%) спирта-->
			<xsl:when test=". = '833'">Гл 100% спирта</xsl:when><!--Гектолитр чистого (100%) спирта-->
			<xsl:when test=". = '841'">кг H<sub>2</sub>О<sub>2</sub></xsl:when><!--Килограмм пероксида водорода-->
			<xsl:when test=". = '845'">кг 90% с/в</xsl:when><!--Килограмм 90%-го сухого вещества-->
			<xsl:when test=". = '847'">т 90% с/в</xsl:when><!--Тонна 90%-го сухого вещества-->
			<xsl:when test=". = '852'">кг К<sub>2</sub>О</xsl:when><!--Килограмм оксида калия-->
			<xsl:when test=". = '859'">кг КОН</xsl:when><!--Килограмм гидроксида калия-->
			<xsl:when test=". = '861'">кг N</xsl:when><!--Килограмм азота-->
			<xsl:when test=". = '863'">кг NaOH</xsl:when><!--Килограмм гидроксида натрия-->
			<xsl:when test=". = '865'">кг Р<sub>2</sub>О<sub>5</sub></xsl:when><!--Килограмм пятиокиси фосфора-->
			<xsl:when test=". = '867'">кг U</xsl:when><!--Килограмм урана-->
			<xsl:when test=". = '018'">пог. м</xsl:when><!--Погонный метр-->
			<xsl:when test=". = '019'">тыс. пог. м</xsl:when><!--Тысяча погонных метров-->
			<xsl:when test=". = '020'">усл. м</xsl:when><!--Условный метр-->
			<xsl:when test=". = '048'">тыс. усл. м</xsl:when><!--Тысяча условных метров-->
			<xsl:when test=". = '049'">км усл. труб</xsl:when><!--Километр условных труб-->
			<xsl:when test=". = '054'">тыс. дм<sup><small>2</small></sup></xsl:when><!--Тысяча квадратных дециметров-->
			<xsl:when test=". = '056'">млн. дм<sup><small>2</small></sup></xsl:when><!--Миллион квадратных дециметров-->
			<xsl:when test=". = '057'">млн. м<sup><small>2</small></sup></xsl:when><!--Миллион квадратных метров-->
			<xsl:when test=". = '060'">тыс. га</xsl:when><!--Тысяча гектаров-->
			<xsl:when test=". = '062'">усл. м<sup><small>2</small></sup></xsl:when><!--Условный квадратный метр-->
			<xsl:when test=". = '063'">тыс. усл. м<sup><small>2</small></sup></xsl:when><!--Тысяча условных квадратных метров-->
			<xsl:when test=". = '064'">млн. усл. м<sup><small>2</small></sup></xsl:when><!--Миллион условных квадратных метров-->
			<xsl:when test=". = '081'">м<sup><small>2</small></sup> общ. пл</xsl:when><!--Квадратный метр общей площади-->
			<xsl:when test=". = '082'">тыс. м<sup><small></small></sup>2 общ. пл</xsl:when><!--Тысяча квадратных метров общей площади-->
			<xsl:when test=". = '083'">млн. м<sup><small>2</small></sup> общ. пл</xsl:when><!--Миллион квадратных метров общей площади-->
			<xsl:when test=". = '084'">м<sup><small>2</small></sup> жил. пл</xsl:when><!--Квадратный метр жилой площади-->
			<xsl:when test=". = '085'">тыс. м<sup><small>2</small></sup> жил. пл</xsl:when><!--Тысяча квадратных метров жилой площади-->
			<xsl:when test=". = '086'">млн. м<sup><small>2</small></sup> жил. пл</xsl:when><!--Миллион квадратных метров жилой площади-->
			<xsl:when test=". = '087'">м<sup><small>2</small></sup> уч. лаб. здан</xsl:when><!--Квадратный метр учебно-лабораторных зданий-->
			<xsl:when test=". = '088'">тыс. м<sup><small>2</small></sup> уч. лаб. здан</xsl:when><!--Тысяча квадратных метров учебно-лабораторных зданий-->
			<xsl:when test=". = '089'">млн. м<sup><small>2</small></sup> 2 мм исч</xsl:when><!--Миллион квадратных метров в двухмиллиметровом исчислении-->
			<xsl:when test=". = '114'">тыс. м<sup><small>3</small></sup></xsl:when><!--Тысяча кубических метров-->
			<xsl:when test=". = '115'">млрд. м<sup><small>3</small></sup></xsl:when><!--Миллиард кубических метров-->
			<xsl:when test=". = '116'">дкл</xsl:when><!--Декалитр-->
			<xsl:when test=". = '119'">тыс. дкл</xsl:when><!--Тысяча декалитров-->
			<xsl:when test=". = '120'">млн. дкл</xsl:when><!--Миллион декалитров-->
			<xsl:when test=". = '121'">плотн. м<sup><small>3</small></sup></xsl:when><!--Плотный кубический метр-->
			<xsl:when test=". = '123'">усл. м<sup><small>3</small></sup></xsl:when><!--Условный кубический метр-->
			<xsl:when test=". = '124'">тыс. усл. м<sup><small>3</small></sup></xsl:when><!--Тысяча условных кубических метров-->
			<xsl:when test=". = '125'">млн. м<sup><small>3</small></sup> перераб. газа</xsl:when><!--Миллион кубических метров переработки газа-->
			<xsl:when test=". = '127'">тыс. плотн. м<sup><small>3</small></sup></xsl:when><!--Тысяча плотных кубических метров-->
			<xsl:when test=". = '128'">тыс. пол. л</xsl:when><!--Тысяча полулитров-->
			<xsl:when test=". = '129'">млн. пол. л</xsl:when><!--Миллион полулитров-->
			<xsl:when test=". = '130'">тыс. л; 1000 л</xsl:when><!--Тысяча литров; 1000 литров-->
			<xsl:when test=". = '165'">тыс. кар</xsl:when><!--Тысяча каратов метрических-->
			<xsl:when test=". = '167'">млн. кар</xsl:when><!--Миллион каратов метрических-->
			<xsl:when test=". = '169'">тыс. т</xsl:when><!--Тысяча тонн-->
			<xsl:when test=". = '171'">млн. т</xsl:when><!--Миллион тонн-->
			<xsl:when test=". = '172'">т усл. топл</xsl:when><!--Тонна условного топлива-->
			<xsl:when test=". = '175'">тыс. т усл. топл</xsl:when><!--Тысяча тонн условного топлива-->
			<xsl:when test=". = '176'">млн. т усл. топл</xsl:when><!--Миллион тонн условного топлива-->
			<xsl:when test=". = '177'">тыс. т единовр. хран</xsl:when><!--Тысяча тонн единовременного хранения-->
			<xsl:when test=". = '178'">тыс. т перераб</xsl:when><!--Тысяча тонн переработки-->
			<xsl:when test=". = '179'">усл. т</xsl:when><!--Условная тонна-->
			<xsl:when test=". = '207'">тыс. ц</xsl:when><!--Тысяча центнеров-->
			<xsl:when test=". = '226'">В.А</xsl:when><!--Вольт-ампер-->
			<xsl:when test=". = '231'">м/ч</xsl:when><!--Метр в час-->
			<xsl:when test=". = '232'">ккал</xsl:when><!--Килокалория-->
			<xsl:when test=". = '233'">Гкал</xsl:when><!--Гигакалория-->
			<xsl:when test=". = '234'">тыс. Гкал</xsl:when><!--Тысяча гигакалорий-->
			<xsl:when test=". = '235'">млн. Гкал</xsl:when><!--Миллион гигакалорий-->
			<xsl:when test=". = '236'">кал/ч</xsl:when><!--Калория в час-->
			<xsl:when test=". = '237'">ккал/ч</xsl:when><!--Килокалория в час-->
			<xsl:when test=". = '238'">Гкал/ч</xsl:when><!--Гигакалория в час-->
			<xsl:when test=". = '239'">тыс. Гкал/ч</xsl:when><!--Тысяча гигакалорий в час-->
			<xsl:when test=". = '241'">млн. А.ч</xsl:when><!--Миллион ампер-часов-->
			<xsl:when test=". = '242'">млн. кВ.А</xsl:when><!--Миллион киловольт-ампер-->
			<xsl:when test=". = '248'">кВ.А Р</xsl:when><!--Киловольт-ампер реактивный-->
			<xsl:when test=". = '249'">млрд. кВт.ч</xsl:when><!--Миллиард киловатт-часов-->
			<xsl:when test=". = '250'">тыс. кВ.А Р</xsl:when><!--Тысяча киловольт-ампер реактивных-->
			<xsl:when test=". = '251'">л. с</xsl:when><!--Лошадиная сила-->
			<xsl:when test=". = '252'">тыс. л. с</xsl:when><!--Тысяча лошадиных сил-->
			<xsl:when test=". = '253'">млн. л. с</xsl:when><!--Миллион лошадиных сил-->
			<xsl:when test=". = '254'">бит</xsl:when><!--Бит-->
			<xsl:when test=". = '255'">байт</xsl:when><!--Байт-->
			<xsl:when test=". = '256'">кбайт</xsl:when><!--Килобайт-->
			<xsl:when test=". = '257'">Мбайт</xsl:when><!--Мегабайт-->
			<xsl:when test=". = '258'">бод</xsl:when><!--Бод-->
			<xsl:when test=". = '287'">Гн</xsl:when><!--Генри-->
			<xsl:when test=". = '313'">Тл</xsl:when><!--Тесла-->
			<xsl:when test=". = '317'">кг/см<sup><small>2</small></sup></xsl:when><!--Килограмм на квадратный сантиметр-->
			<xsl:when test=". = '337'">мм вод. ст</xsl:when><!--Миллиметр водяного столба-->
			<xsl:when test=". = '338'">мм рт. ст</xsl:when><!--Миллиметр ртутного столба-->
			<xsl:when test=". = '339'">см вод. ст</xsl:when><!--Сантиметр водяного столба-->
			<xsl:when test=". = '352'">мкс</xsl:when><!--Микросекунда-->
			<xsl:when test=". = '353'">млс</xsl:when><!--Миллисекунда-->
			<xsl:when test=". = '383'">руб</xsl:when><!--Рубль-->
			<xsl:when test=". = '384'">тыс. руб</xsl:when><!--Тысяча рублей-->
			<xsl:when test=". = '385'">млн. руб</xsl:when><!--Миллион рублей-->
			<xsl:when test=". = '386'">млрд. руб</xsl:when><!--Миллиард рублей-->
			<xsl:when test=". = '387'">трлн. руб</xsl:when><!--Триллион рублей-->
            <xsl:when test=". = '388'">Квадрильон руб</xsl:when><!--Квадрильон рублей-->
			<xsl:when test=". = '414'">пасс.км</xsl:when><!--Пассажиро-километр-->
			<xsl:when test=". = '421'">пасс. мест</xsl:when><!--Пассажирское место (пассажирских мест)-->
			<xsl:when test=". = '423'">тыс. пасс.км</xsl:when><!--Тысяча пассажиро-километров-->
			<xsl:when test=". = '424'">млн. пасс. км</xsl:when><!--Миллион пассажиро-километров-->
			<xsl:when test=". = '427'">пасс.поток</xsl:when><!--Пассажиропоток-->
			<xsl:when test=". = '449'">т.км</xsl:when><!--Тонно-километр-->
			<xsl:when test=". = '450'">тыс. т.км</xsl:when><!--Тысяча тонно-километров-->
			<xsl:when test=". = '451'">млн. т. км</xsl:when><!--Миллион тонно-километров-->
			<xsl:when test=". = '479'">тыс. набор</xsl:when><!--Тысяча наборов-->
			<xsl:when test=". = '510'">г/кВт.ч</xsl:when><!--Грамм на киловатт-час-->
			<xsl:when test=". = '511'">кг/Гкал</xsl:when><!--Килограмм на гигакалорию-->
			<xsl:when test=". = '512'">т.ном</xsl:when><!--Тонно-номер-->
			<xsl:when test=". = '513'">авто т</xsl:when><!--Автотонна-->
			<xsl:when test=". = '514'">т.тяги</xsl:when><!--Тонна тяги-->
			<xsl:when test=". = '515'">дедвейт.т</xsl:when><!--Дедвейт-тонна-->
			<xsl:when test=". = '516'">т.танид</xsl:when><!--Тонно-танид-->
			<xsl:when test=". = '521'">чел/м<sup><small>2</small></sup></xsl:when><!--Человек на квадратный метр-->
			<xsl:when test=". = '522'">чел/км<sup><small>2</small></sup></xsl:when><!--Человек на квадратный километр-->
			<xsl:when test=". = '534'">т/ч</xsl:when><!--Тонна в час-->
			<xsl:when test=". = '535'">т/сут</xsl:when><!--Тонна в сутки-->
			<xsl:when test=". = '536'">т/смен</xsl:when><!--Тонна в смену-->
			<xsl:when test=". = '537'">тыс. т/сез</xsl:when><!--Тысяча тонн в сезон-->
			<xsl:when test=". = '538'">тыс. т/год</xsl:when><!--Тысяча тонн в год-->
			<xsl:when test=". = '539'">чел.ч</xsl:when><!--Человеко-час-->
			<xsl:when test=". = '540'">чел.дн</xsl:when><!--Человеко-день-->
			<xsl:when test=". = '541'">тыс. чел.дн</xsl:when><!--Тысяча человеко-дней-->
			<xsl:when test=". = '542'">тыс. чел.ч</xsl:when><!--Тысяча человеко-часов-->
			<xsl:when test=". = '543'">тыс. усл. банк/ смен</xsl:when><!--Тысяча условных банок в смену-->
			<xsl:when test=". = '544'">млн. ед/год</xsl:when><!--Миллион единиц в год-->
			<xsl:when test=". = '545'">посещ/смен</xsl:when><!--Посещение в смену-->
			<xsl:when test=". = '546'">тыс. посещ/смен</xsl:when><!--Тысяча посещений в смену-->
			<xsl:when test=". = '547'">пар/смен</xsl:when><!--Пара в смену-->
			<xsl:when test=". = '548'">тыс. пар/смен</xsl:when><!--Тысяча пар в смену-->
			<xsl:when test=". = '550'">млн. т/год</xsl:when><!--Миллион тонн в год-->
			<xsl:when test=". = '552'">т перераб/сут</xsl:when><!--Тонна переработки в сутки-->
			<xsl:when test=". = '553'">тыс. т перераб/ сут</xsl:when><!--Тысяча тонн переработки в сутки-->
			<xsl:when test=". = '554'">ц перераб/сут</xsl:when><!--Центнер переработки в сутки-->
			<xsl:when test=". = '555'">тыс. ц перераб/ сут</xsl:when><!--Тысяча центнеров переработки в сутки-->
			<xsl:when test=". = '556'">тыс. гол/год</xsl:when><!--Тысяча голов в год-->
			<xsl:when test=". = '557'">млн. гол/год</xsl:when><!--Миллион голов в год-->
			<xsl:when test=". = '558'">тыс. птицемест</xsl:when><!--Тысяча птицемест-->
			<xsl:when test=". = '559'">тыс. кур. несуш</xsl:when><!--Тысяча кур-несушек-->
			<xsl:when test=". = '2541'">бит/с</xsl:when><!--Бит в секунду-->
			<xsl:when test=". = '2543'">кбит/с</xsl:when><!--Килобит в секунду-->
			<xsl:when test=". = '561'">тыс. т пар/ч</xsl:when><!--Тысяча тонн пара в час-->
			<xsl:when test=". = '562'">тыс. пряд.верет</xsl:when><!--Тысяча прядильных веретен-->
			<xsl:when test=". = '563'">тыс. пряд.мест</xsl:when><!--Тысяча прядильных мест-->
			<xsl:when test=". = '639'">доз</xsl:when><!--Доза-->
			<xsl:when test=". = '640'">тыс. доз</xsl:when><!--Тысяча доз-->
			<xsl:when test=". = '642'">ед</xsl:when><!--Единица-->
			<xsl:when test=". = '643'">тыс. ед</xsl:when><!--Тысяча единиц-->
			<xsl:when test=". = '644'">млн. ед</xsl:when><!--Миллион единиц-->
			<xsl:when test=". = '661'">канал</xsl:when><!--Канал-->
			<xsl:when test=". = '673'">тыс. компл</xsl:when><!--Тысяча комплектов-->
			<xsl:when test=". = '698'">мест</xsl:when><!--Место-->
			<xsl:when test=". = '699'">тыс. мест</xsl:when><!--Тысяча мест-->
			<xsl:when test=". = '709'">тыс. ном</xsl:when><!--Тысяча номеров-->
			<xsl:when test=". = '724'">тыс. га порц</xsl:when><!--Тысяча гектаров порций-->
			<xsl:when test=". = '729'">тыс. пач</xsl:when><!--Тысяча пачек-->
			<xsl:when test=". = '744'">%</xsl:when><!--Процент-->
			<xsl:when test=". = '746'">‰</xsl:when><!--Промилле (0,1 процента)-->
			<xsl:when test=". = '751'">тыс. рул</xsl:when><!--Тысяча рулонов-->
			<xsl:when test=". = '761'">тыс. стан</xsl:when><!--Тысяча станов-->
			<xsl:when test=". = '762'">станц</xsl:when><!--Станция-->
			<xsl:when test=". = '775'">тыс. тюбик</xsl:when><!--Тысяча тюбиков-->
			<xsl:when test=". = '776'">тыс. усл.туб</xsl:when><!--Тысяча условных тубов-->
			<xsl:when test=". = '779'">млн. упак</xsl:when><!--Миллион упаковок-->
			<xsl:when test=". = '782'">тыс. упак</xsl:when><!--Тысяча упаковок-->
			<xsl:when test=". = '792'">чел</xsl:when><!--Человек-->
			<xsl:when test=". = '793'">тыс. чел</xsl:when><!--Тысяча человек-->
			<xsl:when test=". = '794'">млн. чел</xsl:when><!--Миллион человек-->
			<xsl:when test=". = '808'">млн. экз</xsl:when><!--Миллион экземпляров-->
			<xsl:when test=". = '810'">яч</xsl:when><!--Ячейка-->
			<xsl:when test=". = '812'">ящ</xsl:when><!--Ящик-->
			<xsl:when test=". = '836'">гол</xsl:when><!--Голова-->
			<xsl:when test=". = '837'">тыс. пар</xsl:when><!--Тысяча пар-->
			<xsl:when test=". = '838'">млн. пар</xsl:when><!--Миллион пар-->
			<xsl:when test=". = '839'">компл</xsl:when><!--Комплект-->
			<xsl:when test=". = '840'">секц</xsl:when><!--Секция-->
			<xsl:when test=". = '868'">бут</xsl:when><!--Бутылка-->
			<xsl:when test=". = '869'">тыс. бут</xsl:when><!--Тысяча бутылок-->
			<xsl:when test=". = '870'">ампул</xsl:when><!--Ампула-->
			<xsl:when test=". = '871'">тыс. ампул</xsl:when><!--Тысяча ампул-->
			<xsl:when test=". = '872'">флак</xsl:when><!--Флакон-->
			<xsl:when test=". = '873'">тыс. флак</xsl:when><!--Тысяча флаконов-->
			<xsl:when test=". = '874'">тыс. туб</xsl:when><!--Тысяча тубов-->
			<xsl:when test=". = '875'">тыс. кор</xsl:when><!--Тысяча коробок-->
			<xsl:when test=". = '876'">усл. ед</xsl:when><!--Условная единица-->
			<xsl:when test=". = '877'">тыс. усл. ед</xsl:when><!--Тысяча условных единиц-->
            <xsl:when test=". = '878'">млн. усл. ед</xsl:when><!--Миллион условных единиц-->
			<xsl:when test=". = '879'">усл. шт</xsl:when><!--Условная штука-->
			<xsl:when test=". = '880'">тыс. усл. шт</xsl:when><!--Тысяча условных штук-->
			<xsl:when test=". = '881'">усл. банк</xsl:when><!--Условная банка-->
			<xsl:when test=". = '882'">тыс. усл. банк</xsl:when><!--Тысяча условных банок-->
			<xsl:when test=". = '883'">млн. усл. банк</xsl:when><!--Миллион условных банок-->
			<xsl:when test=". = '884'">усл. кус</xsl:when><!--Условный кусок-->
			<xsl:when test=". = '885'">тыс. усл. кус</xsl:when><!--Тысяча условных кусков-->
			<xsl:when test=". = '886'">млн. усл. кус</xsl:when><!--Миллион условных кусков-->
			<xsl:when test=". = '887'">усл. ящ</xsl:when><!--Условный ящик-->
			<xsl:when test=". = '888'">тыс. усл. ящ</xsl:when><!--Тысяча условных ящиков-->
			<xsl:when test=". = '889'">усл. кат</xsl:when><!--Условная катушка-->
			<xsl:when test=". = '890'">тыс. усл. кат</xsl:when><!--Тысяча условных катушек-->
			<xsl:when test=". = '891'">усл. плит</xsl:when><!--Условная плитка-->
			<xsl:when test=". = '892'">тыс. усл. плит</xsl:when><!--Тысяча условных плиток-->
			<xsl:when test=". = '893'">усл. кирп</xsl:when><!--Условный кирпич-->
			<xsl:when test=". = '894'">тыс. усл. кирп</xsl:when><!--Тысяча условных кирпичей-->
			<xsl:when test=". = '895'">млн. усл. кирп</xsl:when><!--Миллион условных кирпичей-->
			<xsl:when test=". = '896'">семей</xsl:when><!--Семья-->
			<xsl:when test=". = '897'">тыс. семей</xsl:when><!--Тысяча семей-->
			<xsl:when test=". = '898'">млн. семей</xsl:when><!--Миллион семей-->
			<xsl:when test=". = '899'">домхоз</xsl:when><!--Домохозяйство-->
			<xsl:when test=". = '900'">тыс. домхоз</xsl:when><!--Тысяча домохозяйств-->
			<xsl:when test=". = '901'">млн. домхоз</xsl:when><!--Миллион домохозяйств-->
			<xsl:when test=". = '902'">учен. мест</xsl:when><!--Ученическое место-->
			<xsl:when test=". = '903'">тыс. учен. мест</xsl:when><!--Тысяча ученических мест-->
			<xsl:when test=". = '904'">раб. мест</xsl:when><!--Рабочее место-->
			<xsl:when test=". = '905'">тыс. раб. мест</xsl:when><!--Тысяча рабочих мест-->
			<xsl:when test=". = '906'">посад. мест</xsl:when><!--Посадочное место-->
			<xsl:when test=". = '907'">тыс. посад. мест</xsl:when><!--Тысяча посадочных мест-->
			<xsl:when test=". = '908'">ном</xsl:when><!--Номер-->
			<xsl:when test=". = '909'">кварт</xsl:when><!--Квартира-->
			<xsl:when test=". = '910'">тыс. кварт</xsl:when><!--Тысяча квартир-->
			<xsl:when test=". = '911'">коек</xsl:when><!--Койка-->
			<xsl:when test=". = '912'">тыс. коек</xsl:when><!--Тысяча коек-->
			<xsl:when test=". = '913'">том книжн. фонд</xsl:when><!--Том книжного фонда-->
			<xsl:when test=". = '914'">тыс. том. книжн. фонд</xsl:when><!--Тысяча томов книжного фонда-->
			<xsl:when test=". = '915'">усл. рем</xsl:when><!--Условный ремонт-->
			<xsl:when test=". = '916'">усл. рем/год</xsl:when><!--Условный ремонт в год-->
			<xsl:when test=". = '917'">смен</xsl:when><!--Смена-->
			<xsl:when test=". = '918'">л. авт</xsl:when><!--Лист авторский-->
			<xsl:when test=". = '920'">л. печ</xsl:when><!--Лист печатный-->
			<xsl:when test=". = '921'">л. уч.-изд</xsl:when><!--Лист учетно-издательский-->
			<xsl:when test=". = '922'">знак</xsl:when><!--Знак-->
			<xsl:when test=". = '923'">слово</xsl:when><!--Слово-->
			<xsl:when test=". = '924'">символ</xsl:when><!--Символ-->
			<xsl:when test=". = '925'">усл. труб</xsl:when><!--Условная труба-->
			<xsl:when test=". = '930'">тыс. пласт</xsl:when><!--Тысяча пластин-->
			<xsl:when test=". = '937'">млн. доз</xsl:when><!--Миллион доз-->
			<xsl:when test=". = '949'">млн. лист.оттиск</xsl:when><!--Миллион листов-оттисков-->
			<xsl:when test=". = '950'">ваг (маш).дн</xsl:when><!--Вагоно(машино)-день-->
			<xsl:when test=". = '951'">тыс. ваг (маш).ч</xsl:when><!--Тысяча вагоно-(машино)-часов-->
			<xsl:when test=". = '952'">тыс. ваг (маш).км</xsl:when><!--Тысяча вагоно-(машино)-километров-->
			<xsl:when test=". = '953'">тыс. мест.км</xsl:when><!--Тысяча место-километров-->
			<xsl:when test=". = '954'">ваг.сут</xsl:when><!--Вагоно-сутки-->
			<xsl:when test=". = '955'">тыс. поезд.ч</xsl:when><!--Тысяча поездо-часов-->
			<xsl:when test=". = '956'">тыс. поезд.км</xsl:when><!--Тысяча поездо-километров-->
			<xsl:when test=". = '957'">тыс. т.миль</xsl:when><!--Тысяча тонно-миль-->
			<xsl:when test=". = '958'">тыс. пасс.миль</xsl:when><!--Тысяча пассажиро-миль-->
			<xsl:when test=". = '959'">автомоб.дн</xsl:when><!--Автомобиле-день-->
			<xsl:when test=". = '960'">тыс. автомоб.т.дн</xsl:when><!--Тысяча автомобиле-тонно-дней-->
			<xsl:when test=". = '961'">тыс. автомоб.ч</xsl:when><!--Тысяча автомобиле-часов-->
			<xsl:when test=". = '962'">тыс. автомоб.мест. дн</xsl:when><!--Тысяча автомобиле-место-дней-->
			<xsl:when test=". = '963'">привед.ч</xsl:when><!--Приведенный час-->
			<xsl:when test=". = '964'">самолет.км</xsl:when><!--Самолето-километр-->
			<xsl:when test=". = '965'">тыс. км</xsl:when><!--Тысяча километров-->
			<xsl:when test=". = '966'">тыс. тоннаж. рейс</xsl:when><!--Тысяча тоннаже-рейсов-->
			<xsl:when test=". = '967'">млн. т. миль</xsl:when><!--Миллион тонно-миль-->
			<xsl:when test=". = '968'">млн. пасс. миль</xsl:when><!--Миллион пассажиро-миль-->
			<xsl:when test=". = '969'">млн. тоннаж. миль</xsl:when><!--Миллион тоннаже-миль-->
			<xsl:when test=". = '970'">млн. пасс. мест. миль</xsl:when><!--Миллион пассажиро-место-миль-->
			<xsl:when test=". = '971'">корм. дн</xsl:when><!--Кормо-день-->
			<xsl:when test=". = '972'">ц корм ед</xsl:when><!--Центнер кормовых единиц-->
			<xsl:when test=". = '973'">тыс. автомоб. км</xsl:when><!--Тысяча автомобиле-километров-->
			<xsl:when test=". = '974'">тыс. тоннаж. сут</xsl:when><!--Тысяча тоннаже-сут-->
			<xsl:when test=". = '975'">суго. сут.</xsl:when><!--Суго-сутки-->
			<xsl:when test=". = '976'">штук в 20-футовом эквиваленте</xsl:when><!--Штук в 20-футовом эквиваленте (ДФЭ)-->
			<xsl:when test=". = '977'">канал. км</xsl:when><!--Канало-километр-->
			<xsl:when test=". = '978'">канал. конц</xsl:when><!--Канало-концы-->
			<xsl:when test=". = '979'">тыс. экз</xsl:when><!--Тысяча экземпляров-->
			<xsl:when test=". = '980'">тыс. доллар</xsl:when><!--Тысяча долларов-->
			<xsl:when test=". = '981'">тыс. корм ед</xsl:when><!--Тысяча тонн кормовых единиц-->
			<xsl:when test=". = '982'">млн. корм ед</xsl:when><!--Миллион тонн кормовых единиц-->
			<xsl:when test=". = '983'">суд.сут</xsl:when><!--Судо-сутки-->
			<xsl:when test=". = '2545'">Мбит/с</xsl:when><!--Мегабит в секунду-->
			<xsl:when test=". = '2547'">Гбит/с</xsl:when><!--Гигабит в секунду-->
			<xsl:when test=". = '2551'">Байт/с</xsl:when><!--Байт в секунду-->
			<xsl:when test=". = '2552'">Гбайт/с</xsl:when><!--Гигабайт в секунду-->
			<xsl:when test=". = '2561'">кбайт/с</xsl:when><!--Килобайт в секунду-->
			<xsl:when test=". = '2571'">Мбайт/с</xsl:when><!--Мегабайт в секунду-->
			<xsl:when test=". = '2581'">Эрл</xsl:when><!--Эрланг-->
			<xsl:when test=". = '276'">Гр</xsl:when><!--Грей-->
			<xsl:when test=". = '3135'">Дб</xsl:when><!--Децибел-->
			<xsl:when test=". = '7923'">Абонент</xsl:when><!--Абонент-->
			<xsl:when test=". = '9061'">млн. га</xsl:when><!--Миллион гектаров-->
			<xsl:when test=". = '9062'">млрд. га</xsl:when><!--Миллиард гектаров-->
			<xsl:when test=". = '9557'">млн. гол</xsl:when><!--Миллион голов-->
			<xsl:when test=". = '9642'">балл</xsl:when><!--Балл-->
			<xsl:when test=". = '9802'">млн. доллар</xsl:when><!--Миллион долларов-->
			<xsl:when test=". = '984'">ц/га</xsl:when><!--Центнеров с гектара-->
			<xsl:when test=". = '985'">тыс. гол</xsl:when><!--Тысяча голов-->
			<xsl:when test=". = '986'">тыс. краск. оттиск</xsl:when><!--Тысяча краско-оттисков -->
			<xsl:when test=". = '987'">млн. краск. оттиск</xsl:when><!--Миллион краско-оттисков-->
			<xsl:when test=". = '988'">млн. усл. плит</xsl:when><!--Миллион условных плиток-->
			<xsl:when test=". = '989'">чел/ч</xsl:when><!--Человек в час-->
			<xsl:when test=". = '990'">пасс/ч</xsl:when><!--Пассажиров в час-->
			<xsl:when test=". = '991'">пасс. миля</xsl:when><!--Пассажиро-миля-->
			<xsl:when test=". = '2553'">Гбайт</xsl:when><!--Гигабайт-->
			<xsl:when test=". = '2554'">Тбайт</xsl:when><!--Терабайт-->
			<xsl:when test=". = '2555'">Пбайт</xsl:when><!--Петабайт-->
			<xsl:when test=". = '2556'">Эбайт</xsl:when><!--Эксабайт-->
			<xsl:when test=". = '2557'">Збайт</xsl:when><!--Зеттабайт-->
			<xsl:when test=". = '2558'">Йбайт</xsl:when><!--Йоттабайт-->
			<xsl:when test=". = '3831'">руб. тонна</xsl:when><!--Рубль тонна-->
			<xsl:when test=". = '5401'">дет. дн</xsl:when><!--Дето-день-->
			<xsl:when test=". = '5423'">чел/год</xsl:when><!--Человек в год-->
			<xsl:when test=". = '5451'">посещ</xsl:when><!--Посещение-->
			<xsl:when test=". = '5562'">тыс. гнезд</xsl:when><!--Тысяча гнезд-->
			<xsl:when test=". = '6421'">ед/год</xsl:when><!--Единиц в год-->
			<xsl:when test=". = '6422'">вызов</xsl:when><!--Вызов-->
			<xsl:when test=". = '6424'">штамм</xsl:when><!--Штамм-->
			<xsl:when test=". = '8361'">ос</xsl:when><!--Особь-->
			<xsl:when test=". = '8751'">кор</xsl:when><!--Коробка-->
			<xsl:when test=". = '9111'">койк. дн</xsl:when><!--Койко-день-->
			<xsl:when test=". = '9113'">пациент. дн</xsl:when><!--Пациенто-день-->
			<xsl:when test=". = '9245'">запись</xsl:when><!--Запись-->
			<xsl:when test=". = '9246'">докум</xsl:when><!--Документ-->
			<xsl:when test=". = '9491'">лист. оттиск</xsl:when><!--Лист-оттиск-->
			<xsl:when test=". = '9501'">ваг (маш) ч</xsl:when><!--Вагоно (машино)-час-->
			<xsl:when test=". = '9641'">летн. ч</xsl:when><!--Летный час-->
			<xsl:when test=". = '9803'">млрд. доллар</xsl:when><!--Миллиард долларов-->
			<xsl:when test=". = '9805'">доллар за тонну</xsl:when><!--Доллар за тонну-->
			<xsl:when test=". = '6423'">пос.ед</xsl:when><!--Посевная единица-->
			<xsl:when test=". = '508'">103 м<sup><small>3</small></sup>/ч</xsl:when><!--Тысяча метров кубических в час-->
			<xsl:when test=". = '164'">мкг</xsl:when><!--Микрограмм-->
			<xsl:when test=". = '303'">кБк</xsl:when><!--Килобеккерель-->
			<xsl:when test=". = '307'">МБк</xsl:when><!--Мегабеккерель-->
			<xsl:when test=". = '320'">моль</xsl:when><!--Моль-->
			<xsl:when test=". = '9910'">МЕ</xsl:when><!--Международная единица биологической активности-->
			<xsl:when test=". = '9911'">тыс. МЕ</xsl:when><!--Тысяча международных единиц биологической активности-->
			<xsl:when test=". = '9912'">млн. МЕ</xsl:when><!--Миллион международных единиц биологической активности-->
			<xsl:when test=". = '9913'">МЕ/г</xsl:when><!--Международная единица биологической активности на грамм-->
			<xsl:when test=". = '9914'">тыс. МЕ/г</xsl:when><!--Тысяча международных единиц биологической активности на грамм-->
			<xsl:when test=". = '9915'">млн. МЕ/г</xsl:when><!--Миллион международных единиц биологической активности на грамм-->
			<xsl:when test=". = '9916'">МЕ/мл</xsl:when><!--Международная единица биологической активности на миллилитр-->
			<xsl:when test=". = '9917'">тыс. МЕ/мл</xsl:when><!--Тысяча международных единиц биологической активности на миллилитр-->
			<xsl:when test=". = '9918'">млн. МЕ/мл</xsl:when><!--Миллион международных единиц биологической активности на миллилитр-->
			<xsl:when test=". = '9920'">ЕД</xsl:when><!--Единица действия биологической активности-->
			<xsl:when test=". = '9921'">ЕД/г</xsl:when><!--Единица биологической активности на грамм-->
			<xsl:when test=". = '9922'">тыс. ЕД/г</xsl:when><!--Тысяча единиц действия биологической активности на грамм-->
			<xsl:when test=". = '9923'">ЕД/мкл</xsl:when><!--Единица действия биологической активности на микролитр-->
			<xsl:when test=". = '9924'">ЕД/мл</xsl:when><!--Единица действия биологической активности на миллилитр-->
			<xsl:when test=". = '9925'">тыс. ЕД/мл</xsl:when><!--Тысяча единиц действия биологической активности на миллилитр-->
			<xsl:when test=". = '9926'">млн. ЕД/мл</xsl:when><!--Миллион единиц действия биологической активности на миллилитр-->
			<xsl:when test=". = '9927'">ЕД/сут</xsl:when><!--Единица действия биологической активности в сутки-->
			<xsl:when test=". = '9930'">АЕ</xsl:when><!--Антитоксическая единица-->
			<xsl:when test=". = '9931'">тыс. АЕ</xsl:when><!--Тысяча антитоксических единиц-->
			<xsl:when test=". = '9940'">АТрЕ</xsl:when><!--Антитрипсиновая единица-->
			<xsl:when test=". = '9941'">тыс. АТрЕ</xsl:when><!--Тысяча антитрипсиновых единиц-->
			<xsl:when test=". = '9950'">ИР</xsl:when><!--Индекс Реактивности-->
			<xsl:when test=". = '9951'">ИР/мл</xsl:when><!--Индекс Реактивности на миллилитр-->
			<xsl:when test=". = '9960'">кБк/мл</xsl:when><!--Килобеккерель на миллилитр-->
			<xsl:when test=". = '9961'">МБк/мл</xsl:when><!--Мегабеккерель на миллилитр-->
			<xsl:when test=". = '9962'">МБк/м<sup><small>2</small></sup></xsl:when><!--Мегабеккерель на метр квадратный-->
			<xsl:when test=". = '9970'">КИЕ/мл</xsl:when><!--Калликреиновая ингибирующая единица на миллилитр-->
			<xsl:when test=". = '9971'">тыс. КИЕ/МЛ</xsl:when><!--Тысяча калликреиновых ингибирующих единиц на миллилитр-->
			<xsl:when test=". = '9980'">млн. КОЕ</xsl:when><!--Миллион колониеобразующих единиц-->
			<xsl:when test=". = '9981'">млн. КОЕ/пакет</xsl:when><!--Миллион колониеобразующих единиц на пакет-->
			<xsl:when test=". = '9982'">млрд. КОЕ</xsl:when><!--Миллиард колониеобразующих единиц-->
			<xsl:when test=". = '9983'">ПЕ</xsl:when><!--Протеолитическая единица-->
			<xsl:when test=". = '9985'">Мкг/мл</xsl:when><!--Микрограмм на миллилитр-->
			<xsl:when test=". = '9986'">Мкг/сут</xsl:when><!--Микрограмм в сутки-->
			<xsl:when test=". = '9987'">Мкг/ч</xsl:when><!--Микрограмм в час-->
			<xsl:when test=". = '9988'">Мкг/доза</xsl:when><!--Микрограмм на дозу-->
			<xsl:when test=". = '9990'">моль/мл</xsl:when><!--Миллимоль на миллилитр-->
			<xsl:when test=". = '9991'">ммоль/л</xsl:when><!--Миллимоль на литр-->
			<xsl:when test=". = '728'">пач</xsl:when><!--Пачка-->
			<xsl:when test=". = '509'">км/сут</xsl:when><!--Километр в сутки-->
			<xsl:when test=". = '277'">мкГр</xsl:when><!--Микрогрей-->
			<xsl:when test=". = '278'">мГр</xsl:when><!--Миллигрей-->
			<xsl:when test=". = '279'">кГр</xsl:when><!--Килогрей-->
			<xsl:when test=". = '293'">ГГц</xsl:when><!--Гигагерц-->
			<xsl:when test=". = '295'">ТГц</xsl:when><!--Терагерц-->
			<xsl:when test=". = '351'">нс</xsl:when><!--Наносекунда-->
			<xsl:when test=". = '318'">Зв</xsl:when><!--Зиверт-->
			<xsl:when test=". = '319'">мкЗв</xsl:when><!--Микрозиверт-->
			<xsl:when test=". = '321'">мЗв</xsl:when><!--Миллизиверт-->
			<xsl:when test=". = '348'">фс</xsl:when><!--Фемтосекунда-->
			<xsl:when test=". = '350'">пс</xsl:when><!--Пикосекунда-->
			<xsl:when test=". = '2311'">Гр/с</xsl:when><!--Грей в секунду-->
			<xsl:when test=". = '2312'">Гр/мин</xsl:when><!--Грей в минуту-->
			<xsl:when test=". = '2313'">Гр/ч</xsl:when><!--Грей в час-->
			<xsl:when test=". = '2314'">мкГр/с</xsl:when><!--Микрогрей в секунду-->
			<xsl:when test=". = '2315'">мкГр/ч</xsl:when><!--Микрогрей в час-->
			<xsl:when test=". = '2316'">мГр/ч</xsl:when><!--Миллигрей в час-->
			<xsl:when test=". = '2351'">Зв/ч</xsl:when><!--Зиверт в час-->
			<xsl:when test=". = '2352'">мкЗв/с</xsl:when><!--Микрозиверт в секунду-->
			<xsl:when test=". = '2353'">мкЗв/ч</xsl:when><!--Микрозиверт в час-->
			<xsl:when test=". = '2354'">мЗв/ч</xsl:when><!--Миллизиверт в час-->
			<xsl:when test=". = '426'">пар груз поезд/сут</xsl:when><!--Пар грузовых поездов в сутки-->
			<xsl:when test=". = '747'">б.п.</xsl:when><!--Базисный пункт-->
			<xsl:when test=". = '340'">г у.т./кВт•ч</xsl:when><!--Грамм условного топлива на киловатт-час-->
			<xsl:when test=". = '341'">кг у.т./Гкал</xsl:when><!--Килограмм условного топлива на гигакалорию-->
			<xsl:when test=". = '9823'">млрд. евро</xsl:when><!--Миллиард евро-->
			<xsl:when test=". = '9822'">млн. евро</xsl:when><!--Миллион евро-->
			<xsl:when test=". = '3181'">чел.-Зв</xsl:when><!--Человеко-зиверт-->
			<xsl:when test=". = '3231'">Бк/м<sup><small>3</small></sup></xsl:when><!--Беккерель на метр кубический-->
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>