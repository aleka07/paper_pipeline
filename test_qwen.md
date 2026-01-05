

> **[Qwen Description]**


Contents lists available at ScienceDirect

## Decision Analytics Journal

journal homepage: www.elsevier.com/locate/dajour

## Digital Twin: Benefits, use cases, challenges, and opportunities

Mohsen Attaran a, ∗ , Bilge Gokhan Celik b

- a Operations Management, School of Business and Public Administration, California State University, Bakersfield, 9001 Stockdale

Highway, CA 93311-1099, United States of America

- b School of Engineering Computing and Construction Management, Roger Williams University, One Old Ferry Road, Bristol, RI 02809, United States of America

## A R T I C L E I N F O

Keywords: Digital Twins Digital Twin Technologies Digital Twin Drivers Healthcare and Life Sciences Automotive and Aerospace Industry Construction and Real Estate

## 1. Introduction

Digital Twin is attracting attention from practitioners and scholars alike. Today, the technology is used across many industries to provide accurate virtual representations of objects and simulations of operational processes. In 2019, a Gartner survey revealed that Digital Twins were entering mainstream use by organizations. It predicted that 75 percent of Internet of Things (IoT) organizations also use Digital Twin technology or plan to use it by 2020 [1,2]. Gartner also estimates that by 2027, over 40 percent of large companies worldwide will be using Digital Twin in their projects to increase revenue [3].

Moreover, Global Market Insight estimated that the Digital Twin market size estimated in 2022 at $8 billion is expected to grow at around 25 percent Compound Annual Growth Rate (CAGR) from 2023 to 2032 [4]. Finally, according to another recent report by global technology research, the Digital Twin market is set to grow by nearly $32 billion from 2021 to 2026 [5]. In addition, according to a 2022 report, nearly 60 percent of executives across a broad spectrum of industry plan to incorporate Digital Twins within their operations by 2028 [6].

## A B S T R A C T

Applications of Digital Twin technology have been growing at an exponential rate, and it is transforming the way businesses operate. In the past few years, Digital Twins leveraged vital business applications, and it is predicted that the technology will expand to more applications, use cases, and industries. The purpose of this paper is to do a literature review and explore how Digital Twins streamline intelligent automation in different industries. This paper defines the concept, highlights the evolution and development of Digital Twins, reviews its key enabling technologies, examines its trends and challenges, and explores its applications in different industries.

The research started by developing key concepts based on a narrative literature review in the Scopus database and Google Scholar and searched for papers that included Digital Twin or Digital Twins in the title. Articles were selected from Journal articles, research articles, conference publications, research reports, or scientific encyclopedias. We reviewed the documents to find answers to the following questions: What is a Digital Twin, what technologies are used, what are the current applications of Digital Twins in different industries, and what are the challenges and opportunities facing this growing technology? We selected research papers that defined the concept, reviewed its related technologies, and highlighted its applications and trends in different industries. Section 2 provides the main perspectives and definitions of Digital Twins in literature. Section 3 reviews four enabling technologies of the Digital Twins. Section 4 studies Digital Twin applications and use cases of different industries. Section 5 highlights the challenges and opportunities of this technology. Finally, Section 6 provides a summary and conclusions. Section 7 provides references.

## 2. Background and definition

Digital Twin is a cutting-edge technology that has revolutionized the industry by mirroring almost every facet of a product, process, or service. It has the potential to replicate everything in the physical world in the digital space and provide engineers with feedback from the virtual world [7]. As a result, the technology enables companies to quickly detect and solve physical problems, design and build better products, and realize value and benefits faster than previously possible. Furthermore, the Digital Twin technology enables businesses to improve business processes and performance [8].

In 2003 Professor Grieves of the University of Michigan introduced the concept of Digital Twins in a total product lifecycle management course. It is also known as a digital mirror and digital mapping. Since then, its definition has continued to evolve as several scholars have provided varied definitions of this technology [9-14]. Encyclopedia of Production Engineering states that '' The Digital Twin is a representation of an active unique ''product'' which can be a real device, object, machine, service, intangible asset, or a system consisting of a product and its related services'' [12]. In general, the Digital Twin is defined as virtual

∗ Corresponding author. E-mail addresses: mattaran@csub.edu (M. Attaran), bgcelik@rwu.edu (B.G. Celik).



> **[Qwen Description]**




> **[Qwen Description]**


Fig. 1. Levels of integration.

This image is a **diagram** that visually categorizes and explains three related concepts in digital representation: **Digital Model**, **Digital Shadow**, and **Digital Twin**. It uses a vertical, hierarchical structure with color-coded arrows on the left and descriptive boxes on the right.

---

### **Structure and Flow**

The diagram is organized from top to bottom, indicating a progression or increasing level of sophistication and interactivity. Each level is connected by a downward-pointing arrow, visually suggesting an evolution or enhancement of the concept.

---

### **Detailed Breakdown by Level**

#### **1. Top Level: Digital Model**
- **Visual Element**: A purple arrow pointing downward, labeled "Digital Model" on its left side.
- **Content Box**: Contains the title "Model" and the description:  
  > *A digital representation of a physical entity*
- **Interpretation**: This is the most basic form — a static or snapshot digital copy of a physical object or system. It serves



> **[Qwen Description]**


representations of physical objects across the lifecycle that can be understood, learned, and reasoned with real-time data or a simulation model that acquires data from the field and triggers the operation of physical devices [15,16].

Furthermore, Digital Twin was defined as the convergence between physical and virtual products [17,18]. Fu et al. [7] thought of the Digital Twin as a real-time digital representation of a physical object. They are remotely connected to real objects and provide rich representations of these objects. They go beyond static product designs, like CAD models, but comprise dynamic behavior [19,20]. A virtual replica of a real-world asset is obtained through constant data transmission allowing the digital version of the object to exist simultaneously with the physical one [17]. Digital Twin uses big data technology to mine hidden and effective data and to improve the intelligence and applicability of Digital Twin technology, especially for quick identification and evaluation of design flaws [21].

Finally, Kritzinger et al. [13] defined Digital Twin, within the field of manufacturing, based on the data integration level, which can be achieved between the physical product and its virtual representation. He identified three levels of integration, The Digital Model, Digital Shadow and the Digital Twin (Fig. 1) [13,22].

A historic early application of Digital Twin technology is when NASA engineers used a simulator, a twin of the command module, and a separate twin of the module's electrical system to remedy and save Apollo 13 in 1970. NASA engineers completed the process in under two hours and saved the lives of the three astronauts on board. This was an extraordinary early application of this technology, and the technology has only matured since then [23]. Today, NASA uses Digital Twins to develop next-generation vehicles and aircraft.

The concept of Digital Twins is not new. However, Digital Twins have moved from idea to reality much faster in recent years. It is predicted that Digital Twins will be combined with more technologies such as speech capabilities, augmented reality, IoT, and artificial intelligence (AI). As a result, Gartner included Digital Twins on its list of top 10 technology trends for 2017 [24]. Gartner also predicted that half of the large industrial firms to use Digital Twins in crucial business applications by 2021 [24]. Finally, MarketsandMarkets research predicted rapid growth for the Digital Twin technology within the next few years, thanks to rising interest in the manufacturing industry to reduce cost and improve supply chain operations. As a result, the market for Digital Twin technology was valued at $6.9 billion in 2022. However, it is expected to reach $73.5 billion by 2027- a CAGR of more than 60 percent [25].

## 3. Digital twin technologies

The three main aspects of Digital Twins are data acquisition, data modeling, and data application [26]. Digital Twin uses four technologies to collect and store real-time data, obtain information to provide valuable insights, and create a digital representation of a physical object. These technologies include the Internet of Things (IoT), Artificial Intelligence (AI), Extended Reality (XR), and Cloud (Fig. 2). In addition, Digital Twin uses a particular technology, depending on the application type, to a greater or lesser extent.

1. Internet of Things (IoT): IoT refers to a giant network of connected ''things''. The connection is between things-things, people-things, or people-people [27]. Digital Twins use IoT as its primary technology in every application. By 2027, more than 90 percent of all IoT platforms will have Digital Twinning capability [6]. IoT uses sensors to collect data from real-world objects. The data transmitted by IoT is used to create a digital duplication of a physical object. The digital version then can then be analyzed, manipulated, and optimized. IoT constantly updates data and helps Digital Twin applications create a real-time virtual representation of a physical object. Therefore, every Digital Twin application uses IoT as a primary technology.
2. Cloud Computing : Cloud computing refers to delivering hosted services over the Internet. The technology efficiently stores and accesses data over the Internet [27]. Cloud computing provides Digital Twins with data computing technology and cloud data storage technology. Cloud computing allows Digital Twin, with large volumes of data, to store data in the virtual Cloud and easily access the required information from any location. Cloud computing enables Digital Twins to effectively reduce the computation time of complex systems and overcome the difficulties of storing large amounts of data [28].
3. Artificial Intelligence (AI): As a discipline of computer science, AI seeks to mimic the basis of intelligence to create a new intelligent machine capable of responding like human-to-human intelligence. Areas of AI study include Robotics, image recognition, and language recognition. Neural Networks, Machine Learning, Deep Learning, and expert systems [29], AI can assist Digital Twins by providing an advanced analytical tool capable of automatically analyzing obtained data and providing valuable insights, making predictions about outcomes, and giving suggestions as to how to avoid potential problems [26].
4. Extended Reality (XR) is an umbrella term used to describe immersive technologies like Virtual Reality (VR), Augmented Reality (AR), and Mixed Reality (MR). These technologies can merge the physical and virtual worlds and extend the reality we experience [30]. XR creates digital representations of objects where digital and real-world objects co-exist and interact in realtime. Digital Twins utilize XR capabilities to digitally model physical objects, allowing users to interact with digital content.

## 4. Digital twins use cases and applications

Today, engineering and manufacturing predominantly use Digital Twins to provide accurate virtual representations of objects and simulations of operational processes. Digital Twins applications in operations and supply chain management, especially the role of Digital Twins in terms of operations traceability, transport maintenance, remote assistance, asset visualization, and design customization, are reviewed in related publications [13,31-38]. The technology is poised to deliver upon its many promises in other industries, including automotive, aerospace, construction, agriculture, mining, utilities, retail, healthcare, military, natural resources, and public safety sectors (Fig. 3) [10,12,19,34,38-44]. The technology has captured the imagination of scholars, managers, and practitioners worldwide, and numerous business applications of this technology are emerging in the literature [10,45-50].

Fig. 4 highlights the impact of Digital Twins solutions on the business world, as explained in the literature and discussed in detail in Section 4.

Fig. 2. Technologies of Digital Twins.

This image is a **diagram** illustrating the core components and their interrelationships that constitute a **Digital Twin** system. It uses a circular, quadrant-based layout to show how four key technologies — IoT, AI, XR, and Cloud — work together around a central concept.

---

### **Overall Structure**

The diagram is centered on a blue sphere labeled **“DIGITAL TWIN”**. Surrounding this central element are four large, colored quadrants, each representing one of the four foundational technologies:

1.  **Top-Left (Dark Blue):** **IOT (Internet of Things)**
2.  **Top-Right (Light Blue):** **AI (Artificial Intelligence)**
3.  **Bottom-Left (Dark Blue):** **XR (Extended Reality)**
4.  **Bottom-Right (Gray):** **Cloud**

Each quadrant has a descriptive text box with a bullet point explaining its function within the Digital Twin ecosystem.

---

### **Detailed



> **[Qwen Description]**


Fig. 3. Industries using Digital Twins.

This image is a **circular diagram** that visually represents the application of a central technology — likely **augmented reality (AR)** or **mixed reality (MR)** — across ten different industries. The diagram is designed to show how this technology is integrated into various sectors, emphasizing its versatility and cross-industry relevance.

---

### **Overall Structure**

- **Central Element**: At the center is a depiction of an AR/MR environment. It shows a person standing in front of a workbench with two robotic arms (one silver, one orange) and a holographic display above the table. The scene suggests a hands-on, immersive experience, possibly for training, maintenance, or remote collaboration.
  
- **Circular Layout**: Surrounding the central image is a ring divided into 10 segments, each representing a different industry. These segments are arranged clockwise and are numbered from 01 to 10.

---

### **Industry Segments (Clockwise from Top Right)**

Each segment contains



> **[Qwen Description]**


innovation [52]. By utilizing the power of the Digital Twin, manufacturing companies can move from being reactive to predictive. They can predict when equipment is wearing down or needs repair, improve the machine's performance, extend their lives and learn how to redesign to do even more. Additionally, Digital Twins enable them to do usagebased design and pre-sales analytics and add intelligence to manual processes to enhance visibility into customer needs, etc. The following sections discuss these capabilities and Digital Twins' usage in more detail.

## 4.1.1. Product design

The introduction of new products or services can have impacts throughout the organization. Furthermore, product and service design has strategic implications for the success of an organization. Consequently, decisions regarding product and service design are among the most fundamental that managers must make. A Digital Twin provides a virtual replica of a manufacturing asset that collects data and provides the ability to create, build, test, and validate predictive analytics and automation [22]. Engineers can use the virtual prototype generated by Digital Twins during the design phase to test different designs

## 4.1. Applications in manufacturing

The manufacturing industry is undergoing a rapid transformation. As a result, interest in exploiting technologies such as Digital Twins in the manufacturing industry is increasing. Digital Twins technology holds great potential for a range of activities in the manufacturing industry and can radically change the face of manufacturing [37,51].

Industry 4.0 have enabled technological advancements in sensing, monitoring, and decision-making tools. These advancements helped the precise implementation of Digital Twin for the real-time monitoring and optimization of the process [35,38]. Fig. 5 highlights the significant technological evolution of Digital Twins over the past four decades [36].

There are many potential use cases for Digital Twinning in manufacturing, including monitoring, simulation, and remote control of physical assets with virtual objects. In addition, Digital Twin technology can assist manufacturing in improving customer satisfaction by better understanding their needs, developing enhancements to existing products, operations, and services, and helping drive new business

## Manufacturing

- Design customization
- Simulate &amp; validate each step of development
- Enhancing Operations Process
- Reducing overall cost of engineering
- predictive maintenance
- Virtually Monitor and manage performance

## Agriculture/Farming

- Advance smart farming
- Plan, monitor, control, analyze &amp; optimize farm processes
- Weather prediction
- Stress identification
- Livestock monitoring &amp; management

## Aerospace/Automotive

- Design customization
- Aircraft tracking
- Defect detection
- Stipulation of weather conditions
- Optimizing the transport load
- Vehicle defect detection
- real-time monitoring and predictive analytics

## Healthcare

- Diagnosis &amp; therapy
- Preventive treatment
- Drug development
- Facility &amp; operations design
- Medical device utilization
- Education &amp; training

## Construction/Real Estate

- Automated Project Control
- Safety monitoring
- Building Performance Assessment
- Project Planning &amp; Logistics
- Evaluate space capacity and smartly design it
- Quality assessment

## Retail

- Supply chain optimization
- Product inception, development &amp; distribution
- Fleet management &amp; route efficiency
- Facility &amp; operations design

Fig. 4. Digital twins use cases and applications.

This image is a **timeline diagram** that illustrates the evolution of a system or field over time, divided into four distinct phases. The diagram uses a horizontal flow with four rectangular nodes connected by arrows, indicating a chronological progression.

---

### **Detailed Description**

The diagram consists of four main rectangular blocks, arranged from left to right, each representing a phase in the development timeline. The blocks are color-coded and contain a time period followed by a descriptive label.

1.  **First Block (Leftmost)**
    *   **Color:** Orange
    *   **Time Period:** 1985–2002
    *   **Label:** "Information Monitoring"
    *   **Description:** This phase represents the initial stage, focused on collecting and observing data.

2.  **Second Block**
    *   **Color:** Light orange
    *   **Time Period:** 2003–2013
    *   **Label:** "Digital



> **[Qwen Description]**


Fig. 5. Evolution of Digital Twins in manufacturing.

before investing in a solid prototype [53]. This reduces the number of prototypes, save time, and reduces production cost. Furthermore, engineers and designers can use data collected over time to improve customer expectations regarding product quality, customization, and ease of use [51].

## 4.1.2. Process design and optimization

Digital Twin helps manufacturers observe processes under multiple performance conditions and eliminate problems before they occur. That allows manufacturers to move from being reactive to predictive. In addition, Digital Twin helps turn existing assets into tools that optimize processes, save money and accelerate innovation [53].

## 4.1.3. Supply chain management

The eternal cycle of rising supply chain costs impacts all players' bottom lines. As a result, manufacturers, retailers, and distributors have identified supply chain cost reduction as critical. Additionally, excellent supply chain performance has a strategic value that could lead to rapid financial payback, often within months, and improvements in productivity and profits [54]. Digital Twin technology can solve supply chain challenges, including packaging performance, fleet management, and route efficiency [55]. Additionally, Digital Twins can help optimize just-in-time or just-in-sequence production and analyze distribution routes. The technology is also helpful in other vital phases of supply chain management, including Product inception, Product development, and Product distribution. More specifically, Digital Twins help to track and analyze packaging performance, fleet management, and route efficiency [56,57].

## 4.1.4. Preventive maintenance

Preventive maintenance focuses on predicting when to schedule maintenance for a component or system to reduce cost and increase machine uptime [58]. Digital Twins can model individual equipment or manufacturing processes to identify variances that indicate the need for preventive repairs or maintenance. The aim is to estimate, predict, detect, or diagnose the condition of a component or a system for maintenance more effectively. This would prevent costly failure before a serious problem occurs. They can also determine if better materials or processes can be utilized or help optimize cycle times, load levels, and tool calibration [41].

## 4.1.5. Cross-functional collaboration

Digital Twins are often used to collect operational data over time. This data provides insights into product performance, distribution, and

## Utilities

- Power grid planning
- Enhanced visibility across physical grid
- Efficiency improvement of the grid
- Power grid self evaluation
- Ecological reconstruction of the grid

## Mining

- Improve machinery productivity
- Allow for realistic simulation training
- Drug development
- Medical device utilization
- Facility &amp; operations design
- Education &amp; training

end-user experience and can be shared by engineering, production, sales, and marketing. Employees across disciplines can all use the same data to make more informed decisions.

## 4.2. Applications in agriculture

The agriculture industry is essential to the functioning of any economy. This industry is an important source of food and raw materials; it is also a vital source of employment opportunities for the total population. The crops, livestock, and seafood produced in the United States, combined with food service and other agriculture-related industries, contribute more than $750 billion annually to the economy [59]. Additionally, the world population is increasing, and market demand for higher product quantity and quality standards is growing, making the issue of food security, sustainability, productivity, and profitability more important. Furthermore, the economic pressure on the agricultural sector and environmental and climate change issues are increasing [60].

## 4.2.1. Farm management, resource optimization

Farming processes are highly complex and dynamic because they depend on natural conditions, such as weather, diseases, soil conditions, seasonality, and climate [61]. Digital Twins technology has the potential to significantly enhance the needed control capabilities of the agricultural industry by enabling the decoupling of physical and information aspects of farm management. The technology can give a virtual representation of a farm with great potential for enhancing efficiency and productivity while reducing energy usage and costs. Although Digital Twin concepts in smart farming are in their infancy and early demonstration stages, many farmers are considering integrating intelligent technologies and techniques that enhance the efficiency of the farming process [39].

## 4.2.2. Weather modeling

An agricultural Digital Twin can also help in weather modeling and prediction of the long-term effects of climate change. Furthermore, Digital Twins allow farmers to identify where and how the agricultural system's resources are stressed by factors such as soil quality, pollution, invasive plants, animals, or other factors [62].

## 4.2.3. Soil management

Digital Twin can assist in measuring and understanding everything we can about the content and capacity of the soil in which crops grow and the seeds and crops that require that soil [62]. Using Digital Twins, the simulated outcomes through a growing season can answer questions about expected yield. The required fertilizer, Sunlight, Water, etc. [43,63,64].

## 4.2.4. Supply chain management

In agriculture food supply chains, customers prioritize the safety of agriculturally produced foods while farmers look for revenue increases. However, the complexities and dynamism of food supply chains put many obstacles to the effectiveness of traceability and management of food products [65]. Therefore, it is critical to have complete visibility into the farm supply chain management to guarantee the food's quality. Digital Twin technology provides the agriculture supply chain with greater traceability and transparency. Furthermore, the utilization of this technology improves the community of the various stakeholders that can support farmers by continuously monitoring physical farms and updating the state of the virtual world [39].

## 4.2.5. Livestock monitoring

Finally, Erdélyi and Jánosi [44] explored the application of Digital Twin for monitoring, managing, and optimizing livestock. Jo et al. [66] proposed Digital Twin technology for simulating the energy consumption of a pigsty to provide decision support for optimal pigsty design. In addition, the same researcher investigated the feasibility of an agricultural Digital Twin for the optimal growth of agricultural livestock, achieved through the regulation of barn systems to maintain air quality and temperature [67].

## 4.3. Healthcare and life sciences

Digital Twin solutions have been widely used in manufacturing and other industries Digital Twins' application in life Sciences mirrors its application in different industries. The applications of Digital Twins technology in the healthcare industry are limitless. The COVID-19 pandemic forced the healthcare and life sciences industry to accelerate its digital transformation efforts [4]. Digital healthcare processes need to become more efficient to support the mass shift to the pandemic. Like any other industry, the life sciences industry is exploring ways to improve efficiency and reduce costs. Now, providers are under pressure to digitally transform and adapt to increasing patient expectations. As a result, interest in exploiting technologies such as Digital Twins in the life sciences is increasing [6].

The technology is increasingly finding use in life sciences applications, especially drug discovery and development [68] For example, an experimental Digital Twin of the human heart comes from a software company 'Dassault.' The company software turns a 2D scan of a human into an accurate full-dimensional model of an individual's heart called "Living Heart''. This realistic human organ model accounts for blood flow, mechanics, and electricity. The Living Heart model is now being used worldwide to create new ways to design and test new devices and drug treatments [69].

Furthermore, Digital Twin solutions are utilized to create replicas and digital models of patients, healthcare facilities, and medical devices. The objectives are to monitor, analyze, and predict issues like personalizing care delivery, predictive maintenance of healthcare facilities, and increasing R&amp;D costs [70].

## 4.3.1. Drug development

We can use the Digital Twin technologies to test new drugs to ascertain drug safety and effectiveness. Each step of the drug development process produces enormous amounts of data that must be managed. Digital Twins use those data to create a model [71]. As a result, Digital Twins can speed up clinical trials in drug research allowing clinical trials to run more quickly, with fewer patients needing to be assigned to receive a drug [72]. Furthermore, Digital Twins will play a key role in developing and producing new vaccines by helping scientists select the best antigen to use, where the development process can also be done virtually.

## 4.3.2. Advanced diagnosis and preventive treatment

Digital Twin technology can simulate various patient characteristics and replicate how they behave and respond in specific situations. This information could help track their health, diagnose diseases, and plan preventive treatments. Additionally, the data obtained from simulation can provide a representative view of a drug's impact on a broader population [71-73].

## 4.3.3. Clinical research

Digital twin technology has the potential to revolutionize the methodology of clinical research. Digital Twins can be used to predict the impact of experimental treatments on a patient, get better answers, and derive actionable insights without risking their life. In addition, the technology helps healthcare professionals study the infected patient's

data for future research in performing treatment simulations and identifying the most promising paths for further research among real people. [4]. For example, a Swedish University has created a Digital Twin of mice affected by rheumatoid arthritis to understand drug efficacy and create a replacement for clinical trials on human beings [70].

## 4.3.4. Personalized medicine

Digital Twin solutions are more accessible and are transforming how the healthcare industry transforms the lives of the people they serve. For example, Digital Twin solutions can be used to fulfill the promise of personalized medicine worldwide [73]. The technology enables physicians to leverage potentially thousands of variables and digital carebacked clinical decision-support solutions to model a patient's best course of treatment intelligently. Additionally, Digital Twin solutions help to study diseases such as Multiple Sclerosis and Alzheimer's to better understand treatment options and reduce trial timelines. Finally, Digital Twin technology can create simulations of new treatments and bring lifesaving innovations to market more quickly. Oklahoma State University's researchers, for example, experimented with a Digital Twin of the respiratory system and simulated aerosol drug particle movements for its delivery in improving lung cancer therapy [70]. Likewise, Siemens developed a Digital Twin of the human heart using millions of images and reports to facilitate an in-depth understanding of heart conditions and predict illness or any underlying health issues. Similarly, a French company developed a Digital Twin of the aneurysm and surrounding blood vessels to enable surgeons to select various patient operating devices based on the Digital Twin study [70].

## 4.3.5. Facility and operations design

As hospitals struggle to lower operating costs and remain competitive, Digital Twin solutions have the potential to reduce costs and improve a patient's journey through a medical facility. Digital Twins can assist healthcare organizations in optimizing hospitals, capacity planning, workflows, staffing systems, and care delivery systems. For example, Digital Twins can mitigate the impact of inaccurate bed occupancy predictions through better predictive analytics based on combining internal and external data-tracking patient flow internally and forecasting potential spikes using external data. Digital Twin, Healthcare providers can use the information provided by Digital Twin solutions to think more strategically about capacity and resources based on better forecasting-improving patient care, operational efficiency, and profitability. Additionally, Digital Twins can be used to model personalized and intelligent medical devices and other equipment to improve efficiency and optimize costs (El Saddik, 2018; [50]). Digital Twins use information gathered by IoT sensors embedded in the device to collect information about the configuration and maintenance history of the device.

## 4.3.6. Education and training

VR technology has been used for decades in medical training, supplementing and enhancing traditional health education. The technology also helped doctors treat patients and surgeons perform robotic surgery. Artificial Intelligence (AI) enabled Digital Twins, using the power of augmented and virtual reality, can facilitate healthcare practitioners' training and education needs. For example, numerous companies have simulated medical anatomy and surgical procedures to inspire interactive learning and minimize the usage of cadavers [48]. Medical schools can use Digital Twin solutions to teach surgical techniques in simulated formats [73].

## 4.3.7. Diagnosis and therapy

Researchers are exploring the use of Digital Twins for advanced understanding of the human body by generating Digital Twins of a single cell, genome, or organs. Digital Twins allow researchers to track patients' health, diagnose diseases, and plan preventive treatments [68]. For example, surgeons can use the virtual digital replica of a patient to plan the surgical procedure and identify the risks associated with the surgery or help mitigate the need for surgery altogether [48,70]. One application of this solution is the National Institute of Health (NIH) Digital Twin models to predict athletes' concussion-related trauma from brain injuries. The data provided by this solution accelerate surgical procedures and speed up recovery plans sim

## 4.4. Automotive &amp; aviation industry

Intense competition among manufacturers for introducing advanced and innovative cars is encouraging companies to invest in the R&amp;D of products and automation of processes. Several automobile manufacturers are adopting upcoming technologies like Digital Twins - using interactive automobile dashboards on websites to improve customer engagement. Customers can customize vehicles at their convenience. Companies use the information to monitor consumer behavior and change existing models [4]. Digital Twin technology is becoming a global area of research where researchers cover Digital Twin implementation on various aspects of intelligent vehicles and explore its potential, opportunities, and challenges to the realization [42].

Digital Twin technology is also widely embraced in the aerospace industry. It is used for aircraft maintenance, tracking, weight monitoring, an accurate stipulation of weather conditions, measurement of flight time, and defect detection [74]. For example, Boeing, the world's largest aerospace company, uses Digital Twin solutions to improve the quality and safety of the parts and systems used to manufacture commercial and military airplanes. As a result, Boeing claims to have achieved a 40 percent improvement in the quality of their airplane parts and systems [75].

## 4.5. Construction and real estate

Using Digital Twins as virtual replicas of physical assets in the construction and real estate industries can revolutionize managing assets and projects. Digital Twins as virtual models of a physical asset have similarities to Building Information Modeling (BIM), which has been used by building industry professionals for many years. Building Information Modeling (BIM) is the digital representation of the physical and functional characteristics of a building or construction project [76]. It provides a shared knowledge resource for information about a building or project, including geometric descriptions, spatial relationships, geographic information, quantities, and properties of building components [77]. While BIM provides static data, Digital Twins, using sensors, provides real-time data that construction managers, designers, or their clients can use to track projects in real-time [78]. Using Digital Twins, construction teams can monitor the construction process, identify potential problems, and adjust strategies to ensure that projects are completed safely, on time, and within budget at the agreed-upon quality. Furthermore, Digital Twin solutions in the construction industry can help track other resources (i.e., materials, labor, equipment), monitor safety, and conduct resource planning and logistics [79].

Digital Twins can provide a comprehensive overview of the physical asset in the real estate industry, allowing agents or property owners to collect and analyze data related to the asset's performance and condition.

In short, using Digital Twins in construction and real estate has the potential to drive unprecedented efficiency in cost, time, sustainability, and safety, making it an invaluable tool for the overall building industry.

## 4.5.1. Automate project control

Digital Twins can help with construction progress tracking by providing real-time insights into the status and performance of construction projects. This can be achieved by integrating data into a virtual model from various sources, such as sensors, drones, laser scanners, and other monitoring systems [80]. Digital Twin solutions powered by

AI can process, analyze, and present the integrated data as an as-built model with daily or hourly comparisons to the baseline model. Such tracking would help solve common construction progress problems by detecting any early deviations from the budget or schedule, allowing project teams to develop and implement any necessary recovery plans.

## 4.5.2. Resource planning and logistics

In the construction industry, unnecessary movement and handling of materials, equipment, and labor can be significant sources of waste. Digital twin solutions can help reduce this waste by enabling a lean approach to resource management. These solutions can provide realtime monitoring of resource allocation and waste tracking, improving the efficiency and productivity of the construction process. One example of the use of Digital Twins for construction progress tracking is the integration of sensor data from construction equipment and vehicles. This can provide real-time information on the location and usage of the assets and help identify potential bottlenecks or inefficiencies. These benefits of Digital Twins would help the construction industry avoid the over-allocation of resources and improve time management [81-84].

## 4.5.3. Construction safety

The safety record of the construction industry is not good. Digital Twins technology combines AI with video cameras, sensors, and mobile devices to build an extensive safety net for the construction workplace [84]. The construction industry can use the real-time site reconstruction feature Digital Twins offer to track and monitor the construction process in real-time, helping to identify and address any issues or deviations from the plan that may pose a safety risk [29]. This information can help prevent the usage of unsafe materials and activity in dangerous zones. In addition, management can create a system of early notification where they are notified if a worker is in danger and send a message to a worker's wearable device [84]. Additionally, upon identifying unsafe behaviors, Digital Twins can be used to provide targeted training for workers in virtual environments, reducing the need for costly and time-consuming physical training and ultimately helping minimize the risk of accidents [29].

## 4.5.4. Quality control and assessment

Digital twin solutions can help with construction quality control and assessment by providing real-time insights into the performance and behavior of the different components and systems of the construction project. Digital twin technology can use image processing algorithms to analyze video or photographic images of a construction site to assess the condition of various components and materials. For example, it can be used to check the concrete condition or identify cracks in columns or other structures. This can help with the detection of potential issues or defects and with the implementation of corrective actions to ensure the quality of the construction process [84].

## 4.5.5. Building performance assessment

Digital twin solutions can be used to assess building performance by simulating the behavior and performance of the building under different conditions and scenarios. This can be achieved by integrating data from various sources, such as sensors, simulations, and BIM models. For example, Digital Twins can be used to analyze the energy efficiency of a building by simulating the consumption and generation of energy and by evaluating the impact of different design and operational strategies. They can also be used to assess the comfort and indoor environmental quality of a building by stimulating the flow of air, heat, and humidity and by evaluating the impact of different design and control strategies [85].

## 4.6. Utilities

The Digital Twin solutions rapidly integrate into the traditional manufacturing industry, smart city, and intelligent power grid [86].

Rapid developments in connectivity through IoT make the potential for Digital Twins dramatically effective within a smart city [87]. The increasing complexity of current power systems makes the digitalization of power assets one of the most discussed topics in the energy sector. Digital Twin technology can be a helpful tool for asset optimization. It can be applied across the whole energy sector to achieve optimal results in terms of maintenance, production planning, plant efficiency, and risk mitigation. A recent study proposed a digital power grid based on Digital Twin technology that can digitize the whole process, all elements, and all services of the physical power grid, such as human and physical events [88]. The digital power grid solution can also help the power grid planning, design, construction, management, and service process [89]. Therefore, it significantly impacts the efficiency improvement of power grid energy resources and information resource allocation [88].

## 4.7. Mining

For the mining industry, several challenges must be addressed if the industry is to maintain a healthy profitability position in the future. The main challenge is to align an environmentally aggressive operation with environmental sustainability issues, energy transition, and greater efficiency in using natural resources. The competitive nature of the industry has been forcing mining companies to optimize the process and improve equipment, productivity, adaptability, and efficiency. In addition, mining companies must embrace the newest technology trends, including Digital Twins, to stay competitive and keep thriving in business [90].

The Digital Twins solution is beneficial for planning schedules and operations in the mining industry. Simulation of the work environment enables miners to create long-term and short-term programs. Additionally, they can make accurate estimates for drilling, crushing, and extraction. Moreover, on-site workers can use Digital Twins solutions to simulate the equipment, machinery, and the entire work process and will be able to test new methodologies on their most crucial work processes. Every test will be executed in a digital simulation in a very cost-effective manner [90].

Digital Twin technology can also enhance the training programs. It allows on-site workers to build a digital training program to help new interns learn the ins and outs of the mining industry, the work they will be executing, and what future possible scenarios they can expect [90].

There are several examples of Digital Twin utilizations in the mining industry. For instance, Rio Tinto has developed a Digital Twin system for its Gudai-Darri iron ore operations, with a value of $2.6 billion. This system allows field personnel and remote operations center staff to access the same real-time data and make informed decisions within seconds rather than waiting for hours or days [91]. Using their Digital Twin system, Rio Tinto (n.d.) has discovered that they can test ways to increase production without jeopardizing equipment or operations.

## 5. Digital twins drivers &amp; challenges

The COVID-19 pandemic fueled the growth of Digital Twin market size across various applications, including real estate, healthcare, energy, and retail, driving the market's growth prospects. As such, several countries are expected to implement Digital Twin solutions as a part of their economic reform activities [92]. Likewise, to recover from economic disruptions caused by the pandemic, several organizations are also adopting Digital Twin technology to optimize their supply chains and operational processes [5].

The current acceleration is mainly made possible by the decreasing costs of technologies that enhance both IoT and the Digital Twin. Furthermore, in the past few years, Digital Twins leveraged vital business applications, and it is predicted that the technology will expand to more use cases, applications, and industries. As a result, applications of Digital Twin technologies have been growing exponentially [39].

Furthermore, cloud companies like Google Cloud and Microsoft Azure are launching cloud-based Digital Twin platforms for easy accessibility and customized solutions. For example, in January 2022, Google Cloud introduced a supply chain Digital Twin solution to provide the manufacturing industry with visibility of operations within their supply chains [92].

The emergence of Industry 4.0 and IoT has also accelerated the adoption of Digital Twin technology across various applications [92]. Industry 4.0 uses innovative production methodologies and advanced technologies, such as cloud computing, IoT, analytics, Digital Twin, digital scanning, 3D printing, and AI. Digital Twin technology is central to the Industry 4.0 initiatives. More and more industries are actively using Digital Twin solutions for asset and product lifecycle management [5]. The technology allows companies to create a virtual replica of their products and processes and empowers them to make the necessary decisions in advance.

As discussed in this article, Digital Twins technology has many advantages; however, the technology currently faces shared challenges in parallel with AI and IoT technologies. Those include data standardization, data management, and data security, as well as barriers to its implementation and legacy system transformation [5]. Other challenges listed in the literature include the need for updating old IT infrastructure, the challenges of connectivity, privacy, and security of sensitive data, and the lack of a standardized modeling approach [10], The significant challenges likely to hamper the growth of the Digital Twin market include the high cost of deployment, increased demand for power and storage, integration challenges with existing systems or proprietary software, and complexity of its architecture. Implementing Digital Twins solutions is costly, requiring significant investment in technology platforms (sensors, software), infrastructure development, maintenance, data quality control, and security solutions. Furthermore, maintaining the Digital Twin infrastructure can be costly, requiring significant investment in operations. The high fixed cost and the complex infrastructure of Digital Twins are expected to slow down the deployment of Digital Twin technologies [5].

## 6. Summary and conclusions

In recent years, Digital Twin technology has garnered significant attention from both industry and academia. There are various definitions for this technology in the literature, as the term is applied to different focus areas within different disciplines. The concept of a Digital Twin can be described as the seamless data integration between a physical and virtual machine in both directions. The Digital Twin technology was first used in the fields of astronautics and aerospace by NASA for the moon exploration mission Apollo 13 and Mars Rover Curiosity. The literature review shows that the breadth and impact of Digital Twins continue to expand, making it a fast-growing IT solution in various industries.

As presented in this paper, most of the manuscripts published in academic journals discuss the application of Digital Twin solutions in manufacturing, particularly within the context of Industry 4.0. Research concerning Digital Twin solutions in manufacturing deals with production planning and control, which plays a central role in integrating all data within a production system. Supply chain management is another area where use cases of Digital Twins are reviewed in the literature. Use cases in the construction and healthcare industry are also growing. In the construction industry, the Digital Twin concept and mobile devices and wearables on a construction site can help better represent the as-built vs. the as-designed project at any given time. In addition, it helps decrease the number of errors and reworks by allowing up-to-date information to be fed back to the field. Digital Twin solutions help the healthcare industry discover undeveloped illnesses, experiment with treatments, and improve surgery preparation. Capturing an accurate full-dimensional human body model will help doctors discover undeveloped illnesses, experiment with treatments, and improve surgery preparation. Researchers are working on developing

Digital Twins to analyze the human body, and significant progressions have been made. Living Heart project is a common technology for clinical diagnosis, testing, medical device design, and education and training. Digital Twin solutions created the first realistic virtual model of a human organ accounting for blood flow, mechanics, and electricity.

Advances in AI, IoT, and cloud computing and the relative strength of these technologies created a groundwork for Digital Twin solutions to evolve quickly and find applications in manufacturing, supply chain, life sciences, agriculture, energy, etc. Artificial Intelligence (AI) enabled Digital Twins to simulate a complex real-world system. It taps into data gathered by IoT devices to learn and run alongside realworld manufacturing systems, continuously identifying improvement areas and supporting tactical decision-making. It also helps optimize systems design to increase efficiency and avoid costly redesign during implementation.

The growing demand for automation in various industries are the anticipated factors to trigger the high demand for the Digital Twin platform over the forecast period. As we recover from the pandemic, Digital Twin solutions are poised to play an increasingly important role in different industries. The benefits of creating a Digital Twin solution are too vast and still not fully explored. While there are challenges to addressing data quality and security, increased demand for power and storage, and integration with existing infrastructures, Digital Twin solutions are thriving to provide a highly advanced digital revolution to make the world a better place for humankind. In the future, Digital Twins will expand to more use cases and industries. The solutions will combine with more technologies, such as augmented reality (AR), for an immersive experience and AI capabilities for better connections, insights, and analytics. In addition, more technologies enable us to use Digital Twin solutions, removing the need to check the 'real' thing. These exponentially higher insights and analytics, in turn, lead to even more possibilities for applications of Digital Twin solutions in complex operations.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Data availability

No data was used for the research described in the article.

## References

- [1] Gartner, Gartner survey reveals digital twins are entering mainstream use, 2019, Online: https://www.gartner.com/en/newsroom/press-releases/2019-0220-gartner-survey-reveals-digital-twins-are-entering-mai.
- [2] Gartner, Gartner survey reveals digital twins are entering mainstream use. February, 2019, Online: https://www.gartner.com/en/newsroom/press-releases/ 2019-02-20-gartner-survey-reveals-digital-twins-are-entering-mai.
- [3] Gartner, Top strategic technology trends, 2023, 2022, Online: https: //emtemp.gcom.cloud/ngw/globalassets/en/publications/documents/2023gartner-top-strategic-technology-trends-ebook.pdf.
- [4] Global Market Insight, Digital twin market. Online, 2022, https://www. gminsights.com/industry-analysis/digital-twin-market.
- [5] Technavio, Digital twin market by end-user, deployment, and geography -Forecast and analysis 2021-2025, 2022, Online: https://finance.yahoo.com/ news/digital-twin-market-size-grow-154500181.html.
- [6] Researchandmarkets, Digital twins market by technology, twinning type, cyberto-physical solutions, use cases and applications in industry verticals 2022-2027, 2022, Online: https://www.researchandmarkets.com/reports/5308850/digitaltwins-market-by-technology-twinning?utm\_source=dynamic&amp;utm\_medium= CI&amp;utm\_code=6q68tb&amp;utm\_campaign=1366076+-The+Future+of+the+ Digital+Twins+Industry+to+2025+in+Manufacturing%2c+Smart+Cities%2c+ Automotive%2c+Healthcare+and+Transport&amp;utm\_exec=joca220cid.
- [7] Y. Fu, G. Zhu, M. Zhu, et al., Digital twin for integration of design-manufacturingmaintenance: An overview, Chin. J. Mech. Eng. 35 (80) (2022) http://dx.doi.org/ 10.1186/s10033-022-00760-x, 2022.

- [8] Qinglin Qi, Fei Tao, Tianliang Hu, Nabil Anwer, Ang Liu, Yongli Wei, Lihui Wang, A.Y.C. Nee, Enabling technologies and tools for digital twin, J. Manuf. Syst. 58 (Part B) 3-21.
- [9] D. Jones, C. Snider, A. Nassehi, J. Yon, B. Hicks, Characterizing the digital twin: A systematic literature review, CIRP J. Manuf. Sci. Technol. 29 (Part A) (2020) 36-52.
- [10] A. Fuller, Z. Fan, C. Day, C. Barlow, Digital twin: Enabling technologies, challenges and open research, IEEE Access 8 (2020) 108952-108971.
- [11] A. Rasheed, O. San, T. Kvamsdal, Digital twin: Values, challenges and enablers from a modeling perspective, IEEE Access 8 (2020) 21980-22012.
- [12] R. Stark, T. Damerau, Digital twin. The international academy for production engineering, in: S. Chatti, T. Tolio (Eds.), CIRP Encyclopedia of Production Engineering, Springer, Berlin Heidelberg, 2019, pp. 1-8.
- [13] W. Kritzinger, M. Karner, G. Traar, J. Henjes, W. Sihn, Digital twin in manufacturing: A categorical literature review and classification, IFAC-PapersOnLine 51 (11) (2018) 1016-1022.
- [14] F. Tao, H. Zhang, A. Liu, A.Y.C. Nee, Digital twin in industry: State-of-the-art, IEEE Trans. Ind. Inf. 15 (4) (2018) 2405-2415.
- [15] R.N. Bolton, J.R. Mccoll-Kennedy, L. Cheung, Customer experience challenges: bringing together digital, physical and social realms, J. Serv. Manag. 29 (5) (2018) 776-808.
- [16] N. Negri, S. Berardi, S. Fumagalli, MES-integrated digital twin frameworks, J. Manuf. Syst. 56 (2020) 58-71.
- [17] M. Grieves, Digital Twin: Manufacturing Excellence Through Virtual Factory Replication, White Paper, 2014, pp. 1-7, Online: https://www.researchgate.net/ publication/275211047\_Digital\_Twin\_Manufacturing\_Excellence\_through\_Virtual\_ Factory\_Replication.
- [18] F. Tao, F.Y. Sui, A. Liu, Digital twin-driven product design framework, Int. J. Prod. Res. 57 (12) (2019) 3935-3953.
- [19] S. Boschert, R. Rosen, Digital twin-The simulation aspect, in: P. Hehenberger, D. Bradley (Eds.), Mechatronic Futures, Springer International Publishing, Switzerland, ISBN: 978-3-319-32154-7, 2016, pp. 59-74, http://dx.doi.org/10.1007/ 978-3-319-32156-1\_5, Chapter 6.
- [20] M. Grieves, L. Vickers, Digital twin: Mitigating unpredictable, undesirable emergent behavior in complex systems, in: Transdisciplinary Perspectives on Complex Systems, Springer, 2017, 2017.
- [21] J. Guo, N. Zhao, L. Sun, Modular based flexible digital twin for factory design, J. Ambient Intell. Humaniz. Comput. 10 (3) (2019) 1189-1200.
- [22] M. Grieves, Digital Twin: Manufacturing Excellence Through Virtual Factory Replication, White Paper, 2015, Online: https://www.3ds.com/fileadmin/ PRODUCTS-SERVICES/DELMIA/PDF/Whitepaper/DELMIA-APRISO-DigitalTwin-Whitepaper.pdf -03-01).
- [23] J. Uri, 50 Years ago: Houston, we've had a problem, 2020, Online: https: //www.nasa.gov/feature/50-years-ago-houston-we-ve-had-a-problem.
- [24] K. Panetta, Gartner's top 10 technology trends 2017, 2016, Online: https://www. gartner.com/smarterwithgartner/gartners-top-10-technology-trends-2017.
- [25] MarketsandMarkets, Digital twin market by enterprise: Application, industry, and geography-global forecast to 2027, 2022, Online: https://www. marketsandmarkets.com/Market-Reports/digital-twin-market-225269522.html.
- [26] Z. Lv, S. Xie, Artificial intelligence in the digital twins: State of the art, challenges, and future research topics, 2021, Online: https://doi.org/10.12688/ digitaltwin.17524.1.
- [27] M. Attaran, The Internet of Things: Limitless opportunities for business and society, J. Strateg. Innov. Sustain. 12 (1) (2017).
- [28] Z. Shu, J. Wan, D. Zhang, Cloud-integrated cyber-physical systems for complex industrial applications, Mob. Netw. Appl. 21 (5) (2016) 865-878.
- [29] L. Hou, S. Wu, G. Zhang, Y. Tan, X. Wang, Literature review of digital twins applications in construction workforce safety, Appl. Sci. 11 (1) (2020) 339.
- [30] B. Marr, What is extended reality technology? A simple explanation for anyone. Aug 12, 2019, 2019, Online: https://www.forbes.com/sites/bernardmarr/ 2019/08/12/what-is-extended-reality-technology-a-simple-explanation-foranyone/?sh=22e4c7117249.
- [31] C. Chiara, N. Elisa, F. Luca, Review of digital twin applications in manufacturing, Comput. Ind. 113 (December) (2019) 103130.
- [32] R. Geng, M. Li, Z. Hu, Z. Han, R. Zheng, Digital twin in smart manufacturing: Remote control and virtual machining using VR and AR technologies, Struct. Multidisc. Optim. 65 (2022) 321.
- [33] V. Havard, B. Jeanne, M. Lacomblez, Baudry D., Digital twin and virtual reality: A co-simulation environment for design and assessment of industrial workstations, Prod. Manuf. Res. 7 (1) (2019) 472-489.
- [34] A. Redelinghuys, A. Basson, K. Kruger, A six-layer digital twin architecture for a manufacturing cell, in: T. Borangiu, D. Trentesaux, A. Thomas, S. Cavalieri (Eds.), Service Orientation in Holonic and Multi-Agent Manufacturing, Springer International Publishing, Cham, 2019, pp. 412-423.
- [35] Q. Qiao, J. Wang, L. Ye, R.X. Gao, Digital twin for machining tool condition prediction, Procedia CIRP 81 (2019) 1388-1393.
- [36] V. Warke, S. Kumar, A. Bongale, K. Kotecha, Sustainable development of smart manufacturing driven by the digital twin framework: A statistical analysis, Sustainability 2021 (2021) 13.
- [37] A. Bilberg, A.A. Malik, Digital twin driven human-robot collaborative assembly, CIRP Ann. 68 (2019) 499-502.
- [38] Q. Qi, F. Tao, Digital twin and big data towards smart manufacturing and industry 4.0: 360-degree comparison, IEEE Access 6 (2018) 3585.
- [39] C. Verdouw, B. Tekinerdogan, A. Beulens, S. Wolfert, Digital twins in smart farming, Agric. Syst. 189 (2021) Online at: https://www.sciencedirect.com/ science//pii/S0308521X20309070?via%3Dihub#bb0095.
- [40] R. Rosen, G.von. Wichert, G. Lo, K. Bettenhausen, About the importance of autonomy and digital twins for the future of manufacturing, in: 15th IFAC Symposium on Information Control Problems in Manufacturing, Ottawa, Vol. 1, 2015, pp. 1-13, 2015.
- [41] R.V. Dinter, B. Tekinerdogan, C. Catal, Predictive maintenance using digital twins: A systematic literature review, Inform. Softw. Technol. 151 (November) (2022) 107008.
- [42] G. Bhatti, H. Mohan, R.R. Singh, Towards the future of smart electric vehicles: Digital twin technology, Renew. Sustain. Energy Rev. 14 (2021).
- [43] R.G. Alves, G. Souza, R.F. Maia, A.L.H. Tran, C. Kamienski, J.P. Soininen, P.T. Aquino, F. Lima, A digital twin for smart farming, in: IEEE Global Humanitarian Technology Conference, GHTC (2019-10), 2019, pp. 1-4.
- [44] V. Erdélyi, L. Jánosi, Digital twin and shadow in smart pork fetteners, Int. J. Eng. Manag. Sci. 4 (1) (2019) 515-520.
- [45] B. Ghanishtha, M. Harshit, R. Singh, Towards the future of smart electric vehicles: Digital twin technology, Renew. Sustain. Energy Rev. 141 (2021) (2021) 110801.
- [46] T. Tao, J. Cheng, Q. Qi, M. Zhang, H. Zhang, F. Sui, Digital twin-driven product design, manufacturing and service with big data, Int. J. Adv. Manuf. Technol. 94 (2018) 3563-3576.
- [47] Y. Liu, Zhang, L. Yang, Y. Zhou, L. Ren, L. Wang, et al., A novel cloud-based framework for the elderly healthcare services using digital twin, IEEE Access 7 (2019) 49088-49101.
- [48] S. Gahlot, Reddy S.R.N., D. Kumar, Review of smart health monitoring approaches with survey analysis and proposed framework, IEEE Internet Things J. 6 (2) (2019) 2116-2127, (2019).
- [49] A. El Saddik, Digital twins: The convergence of multimedia technologies, IEEE MultimediaMag. 25 (2) (2018) 87-92, April.
- [50] D. Ross, Digital twinning information technology virtual reality, Eng. Technol. 11 (2016) 44-45.
- [51] B. Tekinerdogan, C. Verdouw, Systems architecture design pattern catalog for developing digital twins, Sensors 20 (2020) 5103.
- [52] Forbs, What is digital twin technology - And why is it so important. March 6, 2017, Online: https://www.forbes.com/sites/bernardmarr/2017/03/06/what-isdigital-twin-technology-and-why-is-it-so-important/?sh=2ece302a2e2a.
- [53] B. Schleich, N. Anwer, L. Mathieu, S. Wartzack, Shaping the digital twin for design and production engineering, CIRP Ann. 66 (1) (2017) 114-144, (2017).
- [54] M. Attaran, S. Attaran, Collaborative supply chain management: The most promising practice for building efficient and sustainable supply chains, Bus. Process Manag. J. (2007).
- [55] Y. Blomkvist, L.E.O Ullemar Loenbom, Improving Supply Chain Visibility Within Logistics by Implementing a Digital Twin: A Case Study at Scania Logistics, KTH Institute of Technology, Stockholm, Sweden, 2020.
- [56] K. Dohrmann, B. Gesing, J. and Ward, Digital twins in logistics - A DHL perspective on the impact of digital twins on the logistics industry, 2019.
- [57] Moshood T.D., G. Nawanir, S. Sorooshian, O. Okfalisa, Digital twins driven supply chain visibility within logistics: A new paradigm for future logistics, Appl. Syst. Innov. 4 (29) (2021) http://dx.doi.org/10.3390/asi4020029.
- [58] Z. Kang, C. Catal, B. Tekinerdogan, Remaining useful life (Rul) prediction of equipment in production lines using artificial neural networks, Sensors 21 (2021) 932.
- [59] USDA, What is agriculture's share of the overall US economy? Econ. Res. Serv. (2016) undated. Online: https://www.ers.usda.gov/data-products/chart-gallery/ gallery/chart-detail/?chartId=58270.
- [60] J. Hatfield, G. Takle, R. Grotjahn, P. Holden, R.C. Izaurralde, T. Mader, E. Marshall, D. Liverman, Ch. 6: Agriculture, in: J.M. Melillo, Terese (T.C.) Richmond, G.W. Yohe (Eds.), Climate Change Impacts in the United States: The Third National Climate Assessment, U.S. Global Change Research Program, 2014, pp. 150-174.
- [61] J.H. Trienekens, J.G.A.J. van der Vorst, C.N. Verdouw, Global food supply chains, in: N.K. van Alfen (Ed.), Encyclopedia of Agriculture and Food Systems, second ed., Academic Press, 2014, pp. 499-517, 2014.
- [62] P. Laryukhin, O. Skobelev, S. Lakhin, V. Grachev, O. Yalovenko, O. Yalovenko, The multi-agent approach for developing a cyber-physical system for managing precise farms with digital twins of the plant, Cybern. Phys. 8 (4) (2019) 257-261.
- [63] W. Purcell, T. Neubauer, Digital twins in agriculture: A state-of-the-art review, Smart Agric. Technol. 3 (February) (2023) 100094.

- [64] A. Ahmed, S. Zulfiqar, A. Ghandar, Y. Chen, M. Hanai, G. Theodoropoulos, Digital twin technology for aquaponics: Towards optimizing food production with dynamic data driven application systems, in: G. Tan, A. Lehmann, Y.M. Teo, W. Cai (Eds.), Methods and Applications for Modeling and Simulation of Complex Systems, Vol. 1094, Springer, Singapore, 2019, pp. 3-14.
- [65] I. Hasan, M. Habib, Blockchain technology to ensure traceability of agriculture supply chain management, Int. Supply Chain Technol. J. 8 (2022) 9.
- [66] S.K. Jo, D.H. Park, H. Park, Y. Kwak, S.-H. Kim, Energy planning of pigsty using digital twin, in: International Conference on Information and Communication Technology Convergence, Vol. (2019-10), ICTC, IEEE, 2019, pp. 723-725.
- [67] Seng-Kyoun. Jo, Dae-Heon. Park, Hyeon. Park, Se-Han. Kim, Smart livestock farms using digital twin: Feasibility study, in: Published in : 2018 International Conference on Information and Communication Technology Convergence, ICTC. 17-19 2018. Jeju, Korea (South), 2018.
- [68] KPMG, The AI-enabled digital twin for life sciences, 2021, Online: https://institutes.kpmg.us/content/dam/institutes/en/healthcare-life-sciences/ pdfs/2021/ai-enabled-digital-twin-life-sciences.pdf.
- [69] Dassault Systems, The living heart project, 2022, Online: https://www.3ds.com/ products-services/simulia/solutions/life-sciences-healthcare/the-living-heartproject/.
- [70] FutureBridge, Digital twin simulating the bright future of healthcare. October 21, 2021, Online: https://www.futurebridge.com/industry/perspectives-lifesciences/digital-twin-simulating-the-bright-future-of-healthcare/.
- [71] K. Subramanian, Digital twin for drug discovery and development-The virtual LiverJ, J. Indian Inst. Sci. 100 (4) (2020) 653-662.
- [72] Forbs, Meet your digital twin: The coming revolution in drug development. September 29, 2021, Online: https://www.forbes.com/sites/ganeskesari/2021/ 09/29/meet-your-digital-twin-the-coming-revolution-in-drug-development/?sh= 67679144745f.
- [73] A. De Benedictis, N. Mazzocca, A. Somma, C. Strigaro, Digital twins in healthcare: an architectural proposal and its application in a social distancing case study, IEEE J. Biomed. Health Inf. XX (XX) (2022) XXXX, Online: https://ieeexplore. ieee.org/stamp/stamp.jsp?arnumber=9882337.
- [74] M. Xiong, H. Wang, Digital twin applications in aviation industry: A review, Int. J. Adv. Manuf. Technol. 121 (9-10) (2022) 1-16.
- [75] B.I.I.I. Woodrow, Boeing CEO talks 'Digital Twin' era of aviation. September 14, 2018, Online: https://www.aviationtoday.com/2018/09/14/boeing-ceotalks-digital-twin-era-aviation/.
- [76] National Institute of Building Sciences, National BIM Standard-United States Version 3. in Section 4.2: Construction Operation Building Information Exchange (COBie)-Version 2.4 (1-252), National Institute of Building Sciences, Washington DC, 2015.
- [77] E.P. Karan, J. Irizarry, Extending BIM interoperability to preconstruction operations using geospatial analyses and semantic web services, Autom. Constr. 53 (2015) 1-12.
- [78] S. Tang, D.R. Shelden, C.M. Eastman, P. Pishdad-Bozorgi, X. Gao, A review of building information modeling (BIM) and the Internet of Things (IoT) devices integration: Present status and future trends, Autom. Constr. 101 (2019) 127-139.
- [79] J.O. De-Graft, S. Perera, R. Osei-Kyei, M. Rashidi, Digital twin application in the construction industry: A literature review, J. Build. Eng. 40 (2021) (August).
- [80] S. Alizadehsalehi, I. Yitmen, Digital twin-based progress monitoring management model through reality capture to extended reality technologies (DRX), Smart Sustain. Built. Environ. (2021).
- [81] R. Sacks, I. Brilakis, E. Pikas, H.S. Xie, M. Girolami, Construction with digital twin information systems, Data-Centric Eng. 1 (2020).
- [82] J. Yang, M.W. Park, P.A. Vela, M. Golparvar-Fard, Construction performance monitoring via still images, time-lapse photos, and video streams: Now, tomorrow, and the future, Adv. Eng. Inform. 29 (2) (2015) 211-224.
- [83] A.A. Akanmu, C.J. Anumba, O.O. Ogunseiju, Towards next generation cyberphysical systems and digital twins for construction, J. Inf. Technol. Constr. 26 (2021) 505-525.
- [84] IntellectSoft, Advanced imaging algorithms in digital twin reconstruction of construction sites. January 17, 2018, Online: https://www.intellectsoft.net/blog/ advanced-imaging-algorithms-for-digital-twin-reconstruction/.
- [85] C.C. Menassa, From BIM to digital twins: A systematic review of the evolution of intelligent building representations in the AEC-FM industry, J. Inform. Technol. Construct. (ITcon) 26 (5) (2021) 58-83.
- [86] H. Bai, Y. Wang, Digital power grid based on digital twin: Definition, structure and key technologies, Energy Rep. (ISSN: 2352-4847) 8 (16) (2022) 390-397.
- [87] N. Mohammadi, J.E. Taylor, Smart city digital twins, in: Proc. IEEE Symp. Ser. Comput. Intell. (SSCI), 1-5, November, 2017.
- [88] A. Francisco, N. Mohammadi, J.E. Taylor, Smart city digital twin-enabled energy management: Toward real-time urban building energy benchmarking, J. Manage Eng. 36 (2) (2020) 04019045.
- [89] H. Pargmann, D. Euhausen, R. Faber, Intelligent big data processing for wind farm monitoring and analysis based on cloud-technologies and digital twins: A quantitative approach, in: Proc. IEEE 3rd Int. Conf. Cloud Comput. Big Data Anal., ICCCBDA, 2018, pp. 233-237, April.
- [90] Deloitte, The net zero workforce: Mining &amp; metals, 2021, Online: https://www2.deloitte.com/content/dam/Deloitte/uk/Documents/energyresources/deloitte-uk-net-zero-workforce-mining-and-metals.pdf.
- [91] Rio Tinto, Innovation. Retrieved January 2, 2023, from https://www.riotinto. com/en/about/innovation.
- [92] Global Market Insight, Digital twin market size, share &amp; trends analysis report by end use (manufacturing, agriculture), by solution (component, process, system), by region (North America, APAC), and segment forecasts, 2022-2030, 2021, Online: https://www.grandviewresearch.com/industryanalysis/digital-twin-market.