# RAG System Benchmark

**Embedding:** text-embedding-3-small  
**LLM:** demo_llm (mock)  
**Total Chunks:** 807  
**Chunker:** SemanticChunker (threshold=0.5, max=800)  

---

## Query #1
**What are all the conditions a student must maintain to stay in good academic standing at VinUni?**

### Search Results (Top 3)
**1.** `score=0.668` | `data\VinPolicys\12_Scholarship_Maintenance_Criteria.md`
> 2.      Maintain good disciplinary standing: The student must not commit major misconduct (Tier 3) or extremely serious misconduct (Tier 4) as per [Student Code of Conduct](https://policy.vinuni.edu.vn/all-policies/student-affairs-regulations-code-of-conduct/) and [Student Academic Integrity](https://policy.vinuni.edu.vn/all-policies/student-academic-integrity/). 3.      Complete the E.X.C.E.L self-evaluation and meet with the Advisor to discuss the self-evaluation.

**2.** `score=0.668` | `data\VinPolicys\12_Scholarship_Maintenance_Criteria.md`
> 2.      Maintain good disciplinary standing: The student must not commit major misconduct (Tier 3) or extremely serious misconduct (Tier 4) as per [Student Code of Conduct](https://policy.vinuni.edu.vn/all-policies/student-affairs-regulations-code-of-conduct/) and [Student Academic Integrity](https://policy.vinuni.edu.vn/all-policies/student-academic-integrity/). 3.      Complete the E.X.C.E.L self-evaluation and meet with the Advisor to discuss the self-evaluation.

**3.** `score=0.654` | `data\VinPolicys\13_Student_Academic_Integrity.md`
> Related Documents - Student Handbook - Academic Regulations - Student Affairs Regulations - Student Code of Conduct Faculty and students can access the [Academic Integrity @ VinUni (sharepoint.com)](https://vinuniversity.sharepoint.com/sites/OfficeofRegistrar/SitePages/Academic-Integrity.aspx) On this site page, you can easily find: - Basic information about academic integrity, violation tiers and respective consequences at VinUni. - Support resources including orientation slides, self-check list, and case studies related to academic integrity.

### Agent Answer
[DEMO LLM] Based on the following context, answer the question.  Context: 2.      Maintain good disciplinary standing: The student must not commit major misconduct (Tier 3) or extremely serious misconduct (Tier 4) as per [Student Code of Conduct](https://policy.vinuni.edu.vn/all-policies/student-affairs-regulations-code-of-conduct/) and [Student Academic Integrity](https://policy.vinuni.edu.vn/all-policies/s...

---

## Query #2
**What safety and conduct regulations must students follow when using VinUni campus facilities?**

### Search Results (Top 3)
**1.** `score=0.711` | `data\VinPolicys\13_Student_Academic_Integrity.md`
> All students and VinUniversity staff and faculty are expected to be familiar with these procedures and follow them as appropriate. ## 2.

**2.** `score=0.687` | `data\VinPolicys\01_Sexual_Misconduct_Response_Guideline.md`
> If VinUni is made aware of an incident of Sexual Misconduct that poses an immediate risk to the physical and mental health and safety of any member of the VinUni Community, VinUni will take steps to protect their health and safety. These measures may encompass temporary suspension from campus activities or making a police report under Section 4.4 of this Policy.

**3.** `score=0.674` | `data\VinPolicys\15_Student_Code_of_Conduct.md`
> All students are expected to comply with this Code and uphold the values of VinUniversity at all times, whether on or off campus. ### 2.1.

### Agent Answer
[DEMO LLM] Based on the following context, answer the question.  Context: All students and VinUniversity staff and faculty are expected to be familiar with these procedures and follow them as appropriate. ## 2.  If VinUni is made aware of an incident of Sexual Misconduct that poses an immediate risk to the physical and mental health and safety of any member of the VinUni Community, VinUni will take steps to ...

---

## Query #3
**What are the admission and language requirements for students entering medical programs at VinUni?**

### Search Results (Top 3)
**1.** `score=0.669` | `data\VinPolicys\06_English_Language_Requirements.md`
> General principles  a. As the medium of instruction at VinUniversity is English, it is important that all admitted students have a suitable proficiency in English to learn and communicate most effectively. VinUniversity will assist candidates who are recommended for admission but do not meet the minimum requirements for admission (refer to conditional admission) to improve their English skills, but students are ultimately responsible for meeting the entry requirements.

**2.** `score=0.667` | `data\VinPolicys\02_Admissions_Regulations_GME_Programs.md`
> e) Certain disciplines may have specific health requirements that will be specified by the Training Institute. Article 6: Admissions Process The admissions process for the GME Program at VinUniversity comprises the following steps:  1. Applicants submit their applications through the online registration portal of VinUniversity.

**3.** `score=0.650` | `data\VinPolicys\02_Admissions_Regulations_GME_Programs.md`
> Article 4: Eligible Candidates Candidates eligible to apply for the GME Program at VinUniversity include doctors who have completed a full-time program in general medical specialties at a recognized medical university, university of medicine and pharmacy, or accredited medical training institutions. Their year of graduation should align with the year of application at VinUniversity.

### Agent Answer
[DEMO LLM] Based on the following context, answer the question.  Context: General principles  a. As the medium of instruction at VinUniversity is English, it is important that all admitted students have a suitable proficiency in English to learn and communicate most effectively. VinUniversity will assist candidates who are recommended for admission but do not meet the minimum requirements for admission (refe...

---

## Query #4
**What procedures and consequences apply when a student breaks university rules?**

### Search Results (Top 3)
**1.** `score=0.646` | `data\VinPolicys\13_Student_Academic_Integrity.md`
> - Dismissal from VinUniversity - Reduction or revoking of financial aid or scholarship - Ban from certain activities or access to certain resources or facilities - Rescinding admission into VinUniversity, a department, program, or internship - Withdrawing or revoking a credential issued by VinUniversity - Other sanction(s) as deemed appropriate by the Council - Tier 4 violations are recorded internally on students’ VinUniversity Student Record on the Student Information System - Upon suspicion of Academic Integrity violation, the instructor will inquire, collect evidence, discuss with the student. - The instructor should take appropriate immediate action to prevent further damage or escalation, including removing the student, taking away/sequestering the paper, etc.

**2.** `score=0.622` | `data\VinPolicys\13_Student_Academic_Integrity.md`
> - The instructor may take action appropriate to the level of the suspected violation, as described in this document. - Cases of major infringements or repeated violations (Tier 4 in Section 5) must be referred to the University Academic Integrity Council with all supporting documents and/or observations.

**3.** `score=0.619` | `data\VinPolicys\13_Student_Academic_Integrity.md`
> Note: Providing contract cheating services to other students is a serious violation of the VinUni Code of Conduct, and will result in severe disciplinary action, up to and including suspension and dismissal. - Immediate suspension (ie. from a final exam) - Suspension can be immediate or for one or more semesters - Failing grade in the course - Removal from course - Written action plan or learning plan required by instructor - The Program Director and instructor may require other remedial actions before the student can enroll in further courses at VinUniversity - Tier 3 cases must be reported to the Registrar using this [e-form](https://forms.office.com/pages/responsepage.aspx?id=iSf4WJVmSk-r2zV2aNVc_0dbBYw8WtJPgbnOOjH80gpUMEk0SUkzWVhQOTIyMk8xWEsxQUNFVEhEMy4u&route=shorturl).

### Agent Answer
[DEMO LLM] Based on the following context, answer the question.  Context: - Dismissal from VinUniversity - Reduction or revoking of financial aid or scholarship - Ban from certain activities or access to certain resources or facilities - Rescinding admission into VinUniversity, a department, program, or internship - Withdrawing or revoking a credential issued by VinUniversity - Other sanction(s) as deemed ap...

---

## Query #5
**How does VinUni evaluate and ensure the quality of its academic programs and teaching staff?**

### Search Results (Top 3)
**1.** `score=0.643` | `data\VinPolicys\15_Student_Code_of_Conduct.md`
> To study and practice according to the academic program and plan of VinUni; to fulfill the students’ duties according to VinUni’s Regulations and Guidelines; to be proactive in self-study, research, and maintain integrity, ethical values and personal conducts. 3.

**2.** `score=0.602` | `data\VinPolicys\15_Student_Code_of_Conduct.md`
> To support and protect the reputation and brand of VinUni, its Colleges, and affiliated academic or support units. 11.

**3.** `score=0.596` | `data\VinPolicys\01_Sexual_Misconduct_Response_Guideline.md`
> 3.4 VinUni will learn through practice to continually improve prevention and response programs and activities. VinUni will build awareness of sexual misconduct through training, education, dialogue, or other means.

### Agent Answer
[DEMO LLM] Based on the following context, answer the question.  Context: To study and practice according to the academic program and plan of VinUni; to fulfill the students’ duties according to VinUni’s Regulations and Guidelines; to be proactive in self-study, research, and maintain integrity, ethical values and personal conducts. 3.  To support and protect the reputation and brand of VinUni, its Colleges,...

---

