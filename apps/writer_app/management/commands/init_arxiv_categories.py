"""
Management command to initialize arXiv categories in the database.

DEPRECATED: arXiv integration moved to separate service.
This command is a stub for backward compatibility.
"""

from django.core.management.base import BaseCommand

# Note: ArxivCategory model removed - arXiv integration delegated to separate service


class Command(BaseCommand):
    help = 'Initialize arXiv categories in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing categories with new information',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing categories before adding new ones',
        )

    def handle(self, *args, **options):
        self.stdout.write('Initializing arXiv categories...')

        if options['clear']:
            self.stdout.write('Clearing existing categories...')
            ArxivCategory.objects.all().delete()
            self.stdout.write(self.style.WARNING('All existing categories cleared.'))

        try:
            with transaction.atomic():
                created_count = self.create_categories(update=options['update'])
                
                if created_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created {created_count} arXiv categories.'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            'No new categories were created. Use --update to update existing categories.'
                        )
                    )

        except Exception as e:
            raise CommandError(f'Error initializing categories: {str(e)}')

    def create_categories(self, update=False):
        """Create arXiv categories based on official arXiv taxonomy."""
        categories_data = [
            # Computer Science
            {
                'code': 'cs.AI',
                'name': 'Artificial Intelligence',
                'description': 'Covers all areas of AI except Vision, Robotics, Machine Learning, Multiagent Systems, and Computation and Language (Natural Language Processing), which have separate subject classes.'
            },
            {
                'code': 'cs.AR',
                'name': 'Hardware Architecture',
                'description': 'Covers systems organization and hardware architecture.'
            },
            {
                'code': 'cs.CC',
                'name': 'Computational Complexity',
                'description': 'Covers models of computation, complexity classes, structural complexity, complexity tradeoffs, upper and lower bounds.'
            },
            {
                'code': 'cs.CE',
                'name': 'Computational Engineering, Finance, and Science',
                'description': 'Covers applications of computer science to the mathematical modeling of complex systems in the fields of science, engineering, and finance.'
            },
            {
                'code': 'cs.CG',
                'name': 'Computational Geometry',
                'description': 'Roughly includes material in ACM Subject Classes I.3.5 and F.2.2.'
            },
            {
                'code': 'cs.CL',
                'name': 'Computation and Language',
                'description': 'Covers natural language processing. Roughly includes material in ACM Subject Class I.2.7.'
            },
            {
                'code': 'cs.CR',
                'name': 'Cryptography and Security',
                'description': 'Covers all areas of cryptography and security including authentication, public key cryptosystems, proof-carrying code, etc.'
            },
            {
                'code': 'cs.CV',
                'name': 'Computer Vision and Pattern Recognition',
                'description': 'Covers image processing, computer vision, pattern recognition, and scene understanding.'
            },
            {
                'code': 'cs.CY',
                'name': 'Computers and Society',
                'description': 'Covers impact of computers on society, computer ethics, information technology and public policy, legal aspects of computing, computers and education.'
            },
            {
                'code': 'cs.DB',
                'name': 'Databases',
                'description': 'Covers database management, datamining, and data processing.'
            },
            {
                'code': 'cs.DC',
                'name': 'Distributed, Parallel, and Cluster Computing',
                'description': 'Covers fault-tolerance, distributed algorithms, stabilization, load balancing, and parallel computation.'
            },
            {
                'code': 'cs.DL',
                'name': 'Digital Libraries',
                'description': 'Covers all aspects of the digital library design and document and text creation.'
            },
            {
                'code': 'cs.DM',
                'name': 'Discrete Mathematics',
                'description': 'Covers combinatorics, graph theory, applications of probability.'
            },
            {
                'code': 'cs.DS',
                'name': 'Data Structures and Algorithms',
                'description': 'Covers data structures and analysis of algorithms.'
            },
            {
                'code': 'cs.ET',
                'name': 'Emerging Technologies',
                'description': 'Covers approaches to information processing (computing, communication, sensing) and bio-chemical analysis based on alternatives to silicon CMOS-based technologies.'
            },
            {
                'code': 'cs.FL',
                'name': 'Formal Languages and Automata Theory',
                'description': 'Covers automata theory, formal language theory, grammars, and other aspects of the theory of computation.'
            },
            {
                'code': 'cs.GL',
                'name': 'General Literature',
                'description': 'Covers introductory material, survey material, predictions of future trends, biographies, and miscellaneous computer-science related material.'
            },
            {
                'code': 'cs.GR',
                'name': 'Graphics',
                'description': 'Covers all aspects of computer graphics.'
            },
            {
                'code': 'cs.GT',
                'name': 'Computer Science and Game Theory',
                'description': 'Covers all theoretical and applied aspects of the intersection of computer science and game theory.'
            },
            {
                'code': 'cs.HC',
                'name': 'Human-Computer Interaction',
                'description': 'Covers human factors, user interfaces, and collaborative computing.'
            },
            {
                'code': 'cs.IR',
                'name': 'Information Retrieval',
                'description': 'Covers indexing, dictionaries, retrieval, content and analysis.'
            },
            {
                'code': 'cs.IT',
                'name': 'Information Theory',
                'description': 'Covers theoretical and experimental aspects of information theory and coding.'
            },
            {
                'code': 'cs.LG',
                'name': 'Machine Learning',
                'description': 'Papers on all aspects of machine learning research (supervised, unsupervised, reinforcement learning, bandit problems, and so on).'
            },
            {
                'code': 'cs.LO',
                'name': 'Logic in Computer Science',
                'description': 'Covers all aspects of logic in computer science, including finite model theory, logics of programs, modal logic, and program verification.'
            },
            {
                'code': 'cs.MA',
                'name': 'Multiagent Systems',
                'description': 'Covers multiagent systems, distributed artificial intelligence, intelligent agents, coordinated interactions, and practical applications.'
            },
            {
                'code': 'cs.MM',
                'name': 'Multimedia',
                'description': 'Covers multimedia information systems and multimedia information representation, processing and retrieval.'
            },
            {
                'code': 'cs.MS',
                'name': 'Mathematical Software',
                'description': 'Roughly includes material in ACM Subject Class G.4.'
            },
            {
                'code': 'cs.NA',
                'name': 'Numerical Analysis',
                'description': 'Covers numerical algorithms for problems in analysis and algebra, scientific computation.'
            },
            {
                'code': 'cs.NE',
                'name': 'Neural and Evolutionary Computing',
                'description': 'Covers neural networks, connectionism, genetic algorithms, artificial life, adaptive behavior.'
            },
            {
                'code': 'cs.NI',
                'name': 'Networking and Internet Architecture',
                'description': 'Covers all aspects of computer communication networks, including network algorithms, protocol design, wireless communication, and network performance.'
            },
            {
                'code': 'cs.OH',
                'name': 'Other Computer Science',
                'description': 'This is the classification to use for documents that do not fit anywhere else.'
            },
            {
                'code': 'cs.OS',
                'name': 'Operating Systems',
                'description': 'Roughly includes material in ACM Subject Classes D.4.1, D.4.2., D.4.3, D.4.4, D.4.5, D.4.7, and D.4.9.'
            },
            {
                'code': 'cs.PF',
                'name': 'Performance',
                'description': 'Covers performance measurement and evaluation, queueing, and simulation.'
            },
            {
                'code': 'cs.PL',
                'name': 'Programming Languages',
                'description': 'Covers programming language semantics, language features, programming approaches (such as object-oriented programming, functional programming, logic programming).'
            },
            {
                'code': 'cs.RO',
                'name': 'Robotics',
                'description': 'Roughly includes material in ACM Subject Class I.2.9.'
            },
            {
                'code': 'cs.SC',
                'name': 'Symbolic Computation',
                'description': 'Roughly includes material in ACM Subject Class I.1.'
            },
            {
                'code': 'cs.SD',
                'name': 'Sound',
                'description': 'Covers all aspects of computing with sound, and sound as an information channel.'
            },
            {
                'code': 'cs.SE',
                'name': 'Software Engineering',
                'description': 'Covers design tools, software metrics, testing and debugging, programming environments, etc.'
            },
            {
                'code': 'cs.SI',
                'name': 'Social and Information Networks',
                'description': 'Covers the design, analysis, and modeling of social and information networks, including their applications for on-line information access, communication, and interaction.'
            },
            {
                'code': 'cs.SY',
                'name': 'Systems and Control',
                'description': 'This section includes theoretical and experimental research covering all facets of automatic control systems.'
            },

            # Mathematics
            {
                'code': 'math.AC',
                'name': 'Commutative Algebra',
                'description': 'Commutative rings, modules, ideals, homological algebra, computational aspects, invariant theory, connections to algebraic geometry and combinatorics.'
            },
            {
                'code': 'math.AG',
                'name': 'Algebraic Geometry',
                'description': 'Algebraic varieties, stacks, sheaves, schemes, moduli spaces, complex geometry, quantum cohomology.'
            },
            {
                'code': 'math.AP',
                'name': 'Analysis of PDEs',
                'description': 'Existence and uniqueness, boundary value problems, linear and non-linear operators, stability, soliton theory, integrable PDE\'s, conservation laws, qualitative dynamics.'
            },
            {
                'code': 'math.AT',
                'name': 'Algebraic Topology',
                'description': 'Homotopy theory, homological algebra, algebraic treatments of manifolds.'
            },
            {
                'code': 'math.CA',
                'name': 'Classical Analysis and ODEs',
                'description': 'Special functions, orthogonal polynomials, harmonic analysis, ODE\'s, differential relations in the complex domain, calculus of variations, approximations, expansions, asymptotics.'
            },
            {
                'code': 'math.CO',
                'name': 'Combinatorics',
                'description': 'Discrete mathematics, graph theory, enumeration, combinatorial optimization, Ramsey theory, combinatorial game theory.'
            },
            {
                'code': 'math.CT',
                'name': 'Category Theory',
                'description': 'Enriched categories, topoi, abelian categories, monoidal categories, homological algebra.'
            },
            {
                'code': 'math.CV',
                'name': 'Complex Variables',
                'description': 'Holomorphic functions, automorphic group actions and forms, pseudoconvexity, complex geometry, analytic spaces, analytic sheaves.'
            },
            {
                'code': 'math.DG',
                'name': 'Differential Geometry',
                'description': 'Complex, contact, Riemannian, pseudo-Riemannian and Finsler geometry, relativity, gauge theory, global analysis.'
            },
            {
                'code': 'math.DS',
                'name': 'Dynamical Systems',
                'description': 'Dynamics of differential equations and flows, mechanics, classical few-body problems, iterations, complex dynamics, delayed differential equations.'
            },
            {
                'code': 'math.FA',
                'name': 'Functional Analysis',
                'description': 'Banach spaces, function spaces, real functions, integral transforms, theory of distributions, measure theory.'
            },
            {
                'code': 'math.GM',
                'name': 'General Mathematics',
                'description': 'Mathematical material of general interest, topics not covered elsewhere.'
            },
            {
                'code': 'math.GN',
                'name': 'General Topology',
                'description': 'Continuum theory, point-set topology, spaces with algebraic structure, foundations, dimension theory, local and global properties.'
            },
            {
                'code': 'math.GR',
                'name': 'Group Theory',
                'description': 'Finite groups, topological groups, representation theory, cohomology, classification and structure.'
            },
            {
                'code': 'math.GT',
                'name': 'Geometric Topology',
                'description': 'Manifolds, orbifolds, polyhedra, cell complexes, foliations, geometric structures.'
            },
            {
                'code': 'math.HO',
                'name': 'History and Overview',
                'description': 'Biographies, philosophy of mathematics, mathematics education, recreational mathematics, communication of mathematics.'
            },
            {
                'code': 'math.IT',
                'name': 'Information Theory',
                'description': 'math.IT is an alias for cs.IT. Covers theoretical and experimental aspects of information theory and coding.'
            },
            {
                'code': 'math.KT',
                'name': 'K-Theory and Homology',
                'description': 'Algebraic and topological K-theory, relations with topology, commutative algebra, and operator algebras.'
            },
            {
                'code': 'math.LO',
                'name': 'Logic',
                'description': 'Logic, set theory, point-set topology, formal mathematics.'
            },
            {
                'code': 'math.MG',
                'name': 'Metric Geometry',
                'description': 'Euclidean, hyperbolic, discrete, convex, coarse geometry, comparisons in Riemannian geometry, symmetric spaces.'
            },
            {
                'code': 'math.MP',
                'name': 'Mathematical Physics',
                'description': 'math.MP is an alias for math-ph. Articles in this category focus on areas of research that illustrate the application of mathematics to problems in physics.'
            },
            {
                'code': 'math.NA',
                'name': 'Numerical Analysis',
                'description': 'math.NA is an alias for cs.NA. Covers numerical algorithms for problems in analysis and algebra, scientific computation.'
            },
            {
                'code': 'math.NT',
                'name': 'Number Theory',
                'description': 'Prime numbers, diophantine equations, analytic number theory, algebraic number theory, arithmetic geometry, Galois theory.'
            },
            {
                'code': 'math.OA',
                'name': 'Operator Algebras',
                'description': 'Algebras of operators on Hilbert space, C^*-algebras, von Neumann algebras, non-commutative geometry.'
            },
            {
                'code': 'math.OC',
                'name': 'Optimization and Control',
                'description': 'Operations research, linear programming, control theory, systems theory, optimal control, game theory.'
            },
            {
                'code': 'math.PR',
                'name': 'Probability',
                'description': 'Theory and applications of probability and stochastic processes: e.g. central limit theorems, large deviations, stochastic differential equations, models from statistical mechanics, queuing theory.'
            },
            {
                'code': 'math.QA',
                'name': 'Quantum Algebra',
                'description': 'Quantum groups, skein theories, operadic and diagrammatic algebra, quantum field theory.'
            },
            {
                'code': 'math.RA',
                'name': 'Rings and Algebras',
                'description': 'Non-commutative rings and algebras, non-associative algebras, universal algebra and lattice theory, linear algebra, semigroups.'
            },
            {
                'code': 'math.RT',
                'name': 'Representation Theory',
                'description': 'Linear representations of algebras and groups, Lie theory, associative algebras, multilinear algebra.'
            },
            {
                'code': 'math.SG',
                'name': 'Symplectic Geometry',
                'description': 'Hamiltonian systems, symplectic flows, classical integrable systems.'
            },
            {
                'code': 'math.SP',
                'name': 'Spectral Theory',
                'description': 'Schrodinger operators, operators on manifolds, general differential operators, numerical studies, integral operators, discrete models, resonances, non-self-adjoint operators, random operators/matrices.'
            },
            {
                'code': 'math.ST',
                'name': 'Statistics Theory',
                'description': 'math.ST is an alias for stat.TH. Applied, computational and theoretical statistics: e.g. statistical inference, regression, time series, multivariate analysis, data mining, Bayesian analysis, resampling, survival analysis, nonparametric and semiparametric methods.'
            },

            # Physics
            {
                'code': 'physics.acc-ph',
                'name': 'Accelerator Physics',
                'description': 'Accelerator theory and simulation. Accelerator technology. Accelerator experiments. Beam Physics. Accelerator design and optimization. Advanced accelerator concepts. Radiation sources including synchrotron light sources and free electron lasers. Applications of accelerators.'
            },
            {
                'code': 'physics.ao-ph',
                'name': 'Atmospheric and Oceanic Physics',
                'description': 'Atmospheric and oceanic physics and physical chemistry, biogeophysics, and climate science.'
            },
            {
                'code': 'physics.app-ph',
                'name': 'Applied Physics',
                'description': 'Applications of physics to new technology, including electronic devices, optics, photonics, microwaves, spintronics, advanced materials, metamaterials, nanotechnology, and energy sciences.'
            },
            {
                'code': 'physics.atm-clus',
                'name': 'Atomic and Molecular Clusters',
                'description': 'Atomic and molecular clusters, nanoparticles: geometric, electronic, optical, chemical, magnetic properties, shell structure, phase transitions, optical spectroscopy, mass spectrometry, photoelectron spectroscopy, ionization, fragmentation, and chemical reactions.'
            },
            {
                'code': 'physics.atom-ph',
                'name': 'Atomic Physics',
                'description': 'Atomic and molecular structure, spectra, collisions, and data. Atoms and molecules in external fields. Molecular dynamics and coherent and incoherent manipulation of atoms and molecules.'
            },
            {
                'code': 'physics.bio-ph',
                'name': 'Biological Physics',
                'description': 'Molecular biophysics, cellular biophysics, neurological biophysics, membrane biophysics, single-molecule biophysics, ecological biophysics, quantum phenomena in biological systems (quantum biology), theoretical biophysics, molecular dynamics/modeling and simulation, game theory, biomechanics, bioinformatics, microorganisms, virology, evolution, biophysical methods.'
            },
            {
                'code': 'physics.chem-ph',
                'name': 'Chemical Physics',
                'description': 'Experimental, computational, and theoretical physics of atoms, molecules, and clusters - Classical and quantum description of states, processes, and dynamics; spectroscopy, electronic structure, conformations, reactions, interactions, and phases.'
            },
            {
                'code': 'physics.class-ph',
                'name': 'Classical Physics',
                'description': 'Newtonian mechanics, classical field theories, waves, fluids, plasma physics, relativity, electromagnetic theory, classical thermodynamics, statistical mechanics, continuum mechanics, classical optics, acoustics and sound, and related areas of classical physics.'
            },
            {
                'code': 'physics.comp-ph',
                'name': 'Computational Physics',
                'description': 'Computational methods in physics and related fields, including numerical computation, computer simulation, computational modeling, algorithm development, and scientific computing.'
            },
            {
                'code': 'physics.data-an',
                'name': 'Data Analysis, Statistics and Probability',
                'description': 'Methods, software and hardware for physics data analysis: data processing and storage; measurement methodology; statistical and mathematical aspects such as parametrization and uncertainties.'
            },
            {
                'code': 'physics.ed-ph',
                'name': 'Physics Education',
                'description': 'Report of results of a research study, coursework, or software/hardware development within the scope of physics education.'
            },
            {
                'code': 'physics.flu-dyn',
                'name': 'Fluid Dynamics',
                'description': 'Turbulence, instabilities, incompressible/compressible flows, reacting flows, geophysical flows, interfacial flows, flows in porous media, micro-flows, biological flows.'
            },
            {
                'code': 'physics.gen-ph',
                'name': 'General Physics',
                'description': 'Description coming soon'
            },
            {
                'code': 'physics.geo-ph',
                'name': 'Geophysics',
                'description': 'Atmospheric physics. Biogeosciences. Computational geophysics. Geographic location. Geoinformatics. Geophysical techniques. Hydrology. Magnetospheric physics. Mathematical geophysics. Planetology. Solar physics. Solid earth geophysics. Space plasma physics.'
            },
            {
                'code': 'physics.hist-ph',
                'name': 'History and Philosophy of Physics',
                'description': 'History and philosophy of physics, astronomy, and cosmology. Biographies, conferences, and other aspects of the physics community.'
            },
            {
                'code': 'physics.ins-det',
                'name': 'Instrumentation and Detectors',
                'description': 'Instrumentation and detectors for research in fundamental physics, astronomy and astrophysics, other areas of applied and engineering physics.'
            },
            {
                'code': 'physics.med-ph',
                'name': 'Medical Physics',
                'description': 'Radiation therapy. Diagnostic radiology. Biomedical imaging modalities (CT, MRI, ultrasound, optical). Image reconstruction and processing. Biomedical system modeling and physiological simulation. Dosimetry. Biomedical radiation effects and safety. Biomedical informatics. Health physics. Monte Carlo medical simulations. Biomedical engineering (involving ionizing and non-ionizing radiations).'
            },
            {
                'code': 'physics.optics',
                'name': 'Optics',
                'description': 'Adaptive optics, astronomical optics, atmospheric optics, biomedical optics, cardinal points, collimation, fiber optics, geometrical optics (Gaussian optics), infrared optics, integrated optics, laser optics, micro-optics, nano-optics, ocean optics, optical materials, optical metrology, optical properties, optical signal processing, optical testing, optical wave propagation, paraxial optics, physical optics, physiological optics, quantum optics, statistical optics, surface optics, ultraviolet optics, visual optics, x-ray optics.'
            },
            {
                'code': 'physics.plasm-ph',
                'name': 'Plasma Physics',
                'description': 'Fundamental plasma physics, magnetic confinement fusion, inertial confinement fusion, plasma physics applications, space plasma physics, astrophysical plasmas.'
            },
            {
                'code': 'physics.pop-ph',
                'name': 'Popular Physics',
                'description': 'Description coming soon'
            },
            {
                'code': 'physics.soc-ph',
                'name': 'Physics and Society',
                'description': 'Structure, dynamics and collective behavior of societies and groups, quantitative sociology and econophysics, computer simulations, socio-economic network topology and dynamics.'
            },
            {
                'code': 'physics.space-ph',
                'name': 'Space Physics',
                'description': 'Heliophysics, solar physics, heliospheric physics, planetary magnetospheres, atmospheric physics, ionospheric physics, plasma physics, planetary rings, cosmic rays, planetary and cometary physics.'
            },

            # Statistics
            {
                'code': 'stat.AP',
                'name': 'Applications',
                'description': 'Biology, Education, Epidemiology, Engineering, Environmental Sciences, Medical, Physical Sciences, Quality Control, Social Sciences.'
            },
            {
                'code': 'stat.CO',
                'name': 'Computation',
                'description': 'Algorithms, Simulation, Visualization.'
            },
            {
                'code': 'stat.ME',
                'name': 'Methodology',
                'description': 'Design, Surveys, Model Selection, Multiple Testing, Multivariate Methods, Signal and Image Processing, Time Series, Smoothing, Spatial Statistics, Survival Analysis, Nonparametric and Semiparametric Methods.'
            },
            {
                'code': 'stat.ML',
                'name': 'Machine Learning',
                'description': 'Covers machine learning papers (supervised, unsupervised, semi-supervised learning, graphical models, reinforcement learning, bandits, high dimensional inference, etc.) with a statistical or theoretical grounding.'
            },
            {
                'code': 'stat.OT',
                'name': 'Other Statistics',
                'description': 'Work in statistics that does not fit into the other stat classifications.'
            },
            {
                'code': 'stat.TH',
                'name': 'Statistics Theory',
                'description': 'stat.TH is an alias for math.ST. Asymptotics, Bayesian Inference, Decision Theory, Estimation, Foundations, Inference, Testing.'
            },

            # Quantitative Biology
            {
                'code': 'q-bio.BM',
                'name': 'Biomolecules',
                'description': 'DNA, RNA, proteins, lipids, etc.; molecular structures and folding kinetics; molecular interactions; single-molecule manipulation.'
            },
            {
                'code': 'q-bio.CB',
                'name': 'Cell Behavior',
                'description': 'Cell-cell signaling and interaction; morphogenesis and development; apoptosis; bacterial conjugation; viral-host interaction; immunology.'
            },
            {
                'code': 'q-bio.GN',
                'name': 'Genomics',
                'description': 'DNA sequencing and assembly; gene and motif finding; RNA editing and alternative splicing; genomic structure and processes (replication, transcription, methylation, etc); mutational processes.'
            },
            {
                'code': 'q-bio.MN',
                'name': 'Molecular Networks',
                'description': 'Gene regulation, signal transduction, proteomics, metabolomics, gene and protein networks.'
            },
            {
                'code': 'q-bio.NC',
                'name': 'Neurons and Cognition',
                'description': 'Synapse, cortex, neuronal dynamics, neural network, sensorimotor control, behavior, attention, decision making, learning, memory, auditory/visual/motor control, computational neuroscience, brain imaging and intervention.'
            },
            {
                'code': 'q-bio.OT',
                'name': 'Other Quantitative Biology',
                'description': 'Work in quantitative biology that does not fit into the other q-bio classifications.'
            },
            {
                'code': 'q-bio.PE',
                'name': 'Populations and Evolution',
                'description': 'Population dynamics, spatio-temporal and epidemiological models, dynamic speciation, co-evolution, biodiversity, foodwebs, aging; molecular evolution and phylogeny; directed evolution; origin of life.'
            },
            {
                'code': 'q-bio.QM',
                'name': 'Quantitative Methods',
                'description': 'All experimental, numerical, statistical and mathematical contributions of value to biology.'
            },
            {
                'code': 'q-bio.SC',
                'name': 'Subcellular Processes',
                'description': 'Assembly and control of subcellular structures (channels, organelles, cytoskeletons, capsules, etc.); molecular motors, transport, subcellular localization; mitosis and meiosis.'
            },
            {
                'code': 'q-bio.TO',
                'name': 'Tissues and Organs',
                'description': 'Blood flow in vessels, biomechanics of bones, electrical waves, endocrine system, tumor growth.'
            },
        ]

        created_count = 0
        for cat_data in categories_data:
            if update:
                category, created = ArxivCategory.objects.update_or_create(
                    code=cat_data['code'],
                    defaults={
                        'name': cat_data['name'],
                        'description': cat_data['description'],
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'Created: {cat_data["code"]} - {cat_data["name"]}')
                else:
                    self.stdout.write(f'Updated: {cat_data["code"]} - {cat_data["name"]}')
            else:
                category, created = ArxivCategory.objects.get_or_create(
                    code=cat_data['code'],
                    defaults={
                        'name': cat_data['name'],
                        'description': cat_data['description'],
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'Created: {cat_data["code"]} - {cat_data["name"]}')

        return created_count