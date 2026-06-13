from pathlib import Path
import sys
import asyncio
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

query = """
Why did modern CPU architectures move from increasing clock speeds to increasing
core counts, and what engineering trade-offs shaped this transition?
"""


async def main(query):
    from retrieval.retrieval_manager import retrivel_search
    print("Retrieval start...")
    retrieval_bundle = await retrivel_search(query)
    results = retrieval_bundle["results"]
   
    print(f"Retrieval complete — {len(results)} results.")
    # pprint(retrieval_result)
    from pprint import pprint
    from postprocessing.reranking_v2 import reranker
    from postprocessing.deduplication import deduplicate
    from postprocessing.fusion import fuse_result
    fused = fuse_result(results)
    if fused is None:
         print("the fused result is empty")
         exit()
    
    retrivel_result_dep = deduplicate(fused)
    if retrivel_result_dep is None:
         print("the deduplicate result is empty")
         exit()
    response = await reranker(retrivel_result_dep)
    print("reranking is completed ")
    
    from generation.prompt_builder import build_prompt
    from generation.context_builder import build_context
    print("context building start")
    context = build_context(response)
    prompt = build_prompt(query,context)
    print("context and prompt are created ! ")
    from llama import generate_answer_llama
    answer = await generate_answer_llama(prompt)

    print("answer is ready \n\n")
    return answer 

if __name__ == "__main__":
    from pprint import pprint
    pprint(asyncio.run(main(query)))   
    # import asyncio
    # asyncio.run(main())  # Single event loop for everything
    

'''

if __name__ == "__main__":
      print("Testing reranker")
      import asyncio
      from pathlib import Path
      import sys

      # Add project root to path
      PROJECT_ROOT = Path(__file__).resolve().parents[1]
      if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
      from retrieval.Unified_retrieval_manager import UnifiedRetrievalResult
      retrivel_result = [UnifiedRetrievalResult(title='Interconnections in Multi-Core Architectures:  '
                                    'Understanding Mechanisms, Overheads and Scaling',
                              url='https://dl.acm.org/doi/10.1145/1080695.1070004',
                              content='Summary:\n'
                                    'The paper analyzes on-chip interconnects in '
                                    'chip multiprocessors, focusing on how '
                                    'interconnect design drives area, power, '
                                    'performance, and overall chip architecture. '
                                    'Key persistent engineering challenges and '
                                    'trade-offs highlighted include:\n'
                                    '\n'
                                    '- Co-design necessity: Interconnect cannot be '
                                    'optimized in isolation; decisions about '
                                    'bandwidth, area, core count, and cache sizing '
                                    'are tightly coupled. Improvements in one '
                                    'dimension (e.g., bandwidth) can constrain '
                                    'others (e.g., cores, cache size) and may not '
                                    'yield proportional performance gains.\n'
                                    '- Scaling limits and non-linear benefits: '
                                    'Simply increasing interconnect bandwidth or '
                                    'speed does not guarantee better performance '
                                    'due to shared resources, coherence overhead, '
                                    'and contention.\n'
                                    '- Coherence and coherence traffic: As core '
                                    'counts grow, maintaining cache coherence '
                                    'becomes a central bottleneck, exacerbated by '
                                    'slower interconnect scaling.\n'
                                    '- Hierarchical vs. flat architectures: '
                                    'Hierarchical bus structures can mitigate some '
                                    'costs of base-line interconnects, reducing '
                                    'coherence traffic and latency while saving '
                                    'area and power compared with a single, fully '
                                    'connected crossbar or flat interconnect.\n'
                                    '- Area and power budgets: Interconnects can '
                                    'consume a significant portion of die area and '
                                    'power, influencing overall design choices and '
                                    'leading to strategies that blend '
                                    'architectural and circuit-level '
                                    'optimizations.\n'
                                    '- Trade-offs in generality vs. '
                                    'specialization: Universal, highly flexible '
                                    'interconnects may incur higher overheads; '
                                    'more specialized, hierarchical designs can '
                                    'offer better performance/power efficiency for '
                                    'common access patterns, at the cost of '
                                    'flexibility.\n'
                                    '- Impact on memory hierarchy: The presence '
                                    'and design of interconnects affect cache '
                                    'hierarchy decisions (e.g., the attractiveness '
                                    'of large shared L2 caches when crossbar '
                                    'overhead is considered).\n'
                                    '\n'
                                    'In short, the evolution toward hierarchical '
                                    'and asynchronous interconnect designs stems '
                                    'from the need to balance speed, distance, '
                                    'power, bandwidth, coherence overhead, and '
                                    'architectural flexibility. Pure scaling of '
                                    'linear models (e.g., naive bandwidth/latency '
                                    'improvements) is insufficient; co-design of '
                                    'interconnect with cores, caches, and '
                                    'coherence protocols yields better overall '
                                    'multi-core performance and efficiency.',
                              provider='exa',
                              query='What persistent engineering challenges and '
                                    'inherent trade-offs (e.g., speed vs. distance, '
                                    'power consumption vs. bandwidth, generality vs. '
                                    'specialization) have driven the evolution of '
                                    'CPU bus architectures towards hierarchical and '
                                    'asynchronous designs, rather than simply '
                                    'scaling initial linear models?',
                              intent='research',
                              priority='high',
                              fusion_score=3,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='Analysis of bus hierarchies for multiprocessors',
                              url='https://dl.acm.org/doi/10.1145/633625.52412',
                              content='Summary:\n'
                                    '\n'
                                    '- The paper analyzes bus-based '
                                    'interconnection networks for large '
                                    'shared-memory multiprocessors, focusing on '
                                    'how to scale beyond a single bus without '
                                    'prohibitive electrical loading.\n'
                                    '- It develops models of bus delay and bus '
                                    'throughput to guide design decisions, '
                                    'enabling the calculation of the maximum '
                                    'number of processors supported by different '
                                    'bus organizations (single-level bus, '
                                    'two-level hierarchies, and binary-tree '
                                    'interconnections).\n'
                                    '- An example using a TTL bus demonstrates '
                                    'that shared-memory multiprocessors with '
                                    'several dozen processors are feasible with a '
                                    'simple two-level bus hierarchy.\n'
                                    '- The broader work (including related '
                                    'material) discusses the performance '
                                    'trade-offs of multilevel bus networks, noting '
                                    'that while multiple buses provide more '
                                    'bandwidth and fault tolerance, scaling '
                                    'becomes expensive due to increased '
                                    'connections and complexity.\n'
                                    '\n'
                                    'Key engineering challenges and trade-offs '
                                    'highlighted (implicit in the evolution toward '
                                    'hierarchical/asynchronous designs):\n'
                                    '- Speed vs. distance: Large single buses '
                                    'suffer from longer electrical propagation '
                                    'paths and loading, degrading speed; '
                                    'hierarchical designs reduce effective length '
                                    'and loading per level.\n'
                                    '- Power and signaling vs. bandwidth: More '
                                    'buses and interconnects raise power '
                                    'consumption and signaling complexity but '
                                    'increase aggregate bandwidth and fault '
                                    'tolerance.\n'
                                    '- Generality vs. specialization: '
                                    'Hierarchical/asynchronous architectures aim '
                                    'for broad coherence and scalability, trading '
                                    'off simplicity of a single, uniform bus for '
                                    'modular, scalable interconnects that can be '
                                    'optimized per level.\n'
                                    '- Feasibility of scaling: Linear models of a '
                                    'single bus become inadequate for large '
                                    'systems; hierarchical/bus-tree or multilevel '
                                    'approaches are required to maintain '
                                    'performance and coherence without prohibitive '
                                    'wiring or latency.\n'
                                    '\n'
                                    'In short, the work argues that to grow '
                                    'CPU/memory coherence beyond dozens of '
                                    'processors, designers must adopt multilevel, '
                                    'hierarchical bus networks (often with '
                                    'asynchronous operation) to balance speed, '
                                    'distance, power, and scalability, rather than '
                                    'attempting to simply scale an initial linear '
                                    'bus model.',
                              provider='exa',
                              query='What persistent engineering challenges and '
                                    'inherent trade-offs (e.g., speed vs. distance, '
                                    'power consumption vs. bandwidth, generality vs. '
                                    'specialization) have driven the evolution of '
                                    'CPU bus architectures towards hierarchical and '
                                    'asynchronous designs, rather than simply '
                                    'scaling initial linear models?',
                              intent='research',
                              priority='high',
                              fusion_score=1,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='Performance Analysis of Multilevel Bus Networks '
                                    'for Hierarchical Multiprocessors | IEEE '
                                    'Transactions on Computers',
                              url='https://dl.acm.org/doi/10.1109/12.293258',
                              content='Summary:\n'
                                    'The paper analyzes multilevel (hierarchical) '
                                    'bus architectures for multiprocessor systems '
                                    'and argues they offer a favorable balance of '
                                    'cost and performance when locality is '
                                    'exploited. Key takeaways relevant to your '
                                    'question about persistent engineering '
                                    'challenges and trade-offs driving '
                                    'hierarchical and asynchronous designs:\n'
                                    '\n'
                                    '- Trade-off: Bandwidth vs. cost and wiring '
                                    'complexity. Fully connected multiple buses '
                                    'give high bandwidth and fault tolerance but '
                                    'require many connections and switches, '
                                    'becoming prohibitively expensive as system '
                                    'size grows. Hierarchical (multilevel) bus '
                                    'architectures reduce connections yet preserve '
                                    'much of the bandwidth when access patterns '
                                    'exhibit locality.\n'
                                    '\n'
                                    '- Locality and nonuniform access: In '
                                    'hierarchical models, processors access nearby '
                                    'memory modules more frequently than distant '
                                    'ones. This nonuniformity motivates designing '
                                    'buses and arbitration to favor local traffic, '
                                    'improving effective bandwidth without a '
                                    'linear growth in interconnection complexity.\n'
                                    '\n'
                                    '- Arbitration and contention: As bus networks '
                                    'scale, arbitration complexity and the '
                                    'efficiency of access control become critical '
                                    'determinants of performance. Efficient bus '
                                    'arbitration mechanisms mitigate contention '
                                    'and help realize near-scalable throughput in '
                                    'hierarchical designs.\n'
                                    '\n'
                                    '- Synchronous vs. asynchronous operation: The '
                                    'work develops models for both synchronous and '
                                    'asynchronous multilevel bus systems, '
                                    'highlighting that asynchronous designs can '
                                    'better tolerate irregular traffic and provide '
                                    'smoother performance under nonuniform '
                                    'workloads, albeit with more complex '
                                    'coordination.\n'
                                    '\n'
                                    '- Performance vs. architectural generality: '
                                    'The multilevel bus system achieves '
                                    'substantial cost savings and improved '
                                    'scalability in the presence of locality, at '
                                    'the expense of some performance loss compared '
                                    'to full-scale multiple-bus systems in '
                                    'worst-case scenarios. This reflects a general '
                                    'engineering trade-off between generic, highly '
                                    'adaptable designs and specialized structures '
                                    'optimized for typical (local) traffic '
                                    'patterns.\n'
                                    '\n'
                                    '- Evolution driver: Beyond raw speed, the '
                                    'evolution toward hierarchical and '
                                    'asynchronous buses has been driven by the '
                                    'need to (a) reduce wiring and switch '
                                    'complexity, (b) manage nonuniform reference '
                                    'patterns, and (c) improve cost-performance '
                                    'under realistic workloads where local memory '
                                    'accesses dominate.\n'
                                    '\n'
                                    'In short, the paper supports the view that as '
                                    'CPU/memory scales, hierarchical and '
                                    'asynchronous bus designs offer a practical '
                                    'path to maintain high effective bandwidth '
                                    'with far fewer interconnections, by '
                                    'exploiting locality and careful arbitration, '
                                    'rather than pursuing naive linear scaling of '
                                    'a single or fully connected bus. This aligns '
                                    'with the broader engineering trend of '
                                    'balancing speed, power, area, and nonuniform '
                                    'traffic in pursuit of scalable, '
                                    'cost-effective parallel architectures.',
                              provider='exa',
                              query='What persistent engineering challenges and '
                                    'inherent trade-offs (e.g., speed vs. distance, '
                                    'power consumption vs. bandwidth, generality vs. '
                                    'specialization) have driven the evolution of '
                                    'CPU bus architectures towards hierarchical and '
                                    'asynchronous designs, rather than simply '
                                    'scaling initial linear models?',
                              intent='research',
                              priority='high',
                              fusion_score=1,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='Constraint-Driven Bus Matrix Synthesis for '
                                    'MPSoC',
                              url='https://www.cecs.uci.edu/conference_proceedings/asp-dac_2006/aspdac06-pasricha-ID1005.pdf',
                              content='Summary:\n'
                                    '\n'
                                    'The work on constraint-driven bus matrix '
                                    'synthesis highlights key engineering '
                                    'challenges and trade-offs that have driven a '
                                    'shift from simple, fully connected (linear) '
                                    'bus models toward hierarchical and more '
                                    'flexible architectures. Core points include:\n'
                                    '\n'
                                    '- Wire congestion and routing feasibility: '
                                    'Full bus matrices connect every master to '
                                    'every slave, causing excessive interconnects '
                                    'that hinder routing, timing closure, and '
                                    'scalability as systems grow.\n'
                                    '\n'
                                    '- Area and power versus performance: A full '
                                    'matrix incurs large area and power due to '
                                    'many busses, arbiters, decoders, and buffers; '
                                    'reducing interconnects (moving to '
                                    'partial/hierarchical structures) lowers area '
                                    'and power but adds design complexity.\n'
                                    '\n'
                                    '- Performance constraints and scalability: '
                                    'Achieving required bandwidth and low latency '
                                    'becomes harder with dense interconnects; '
                                    'hierarchical/partial crossbars and '
                                    'asynchronous-like partitioning help sustain '
                                    'throughput while controlling complexity.\n'
                                    '\n'
                                    '- Design space complexity and automation '
                                    'needs: The number of possible topologies and '
                                    'parameter choices (bus widths, clock speeds, '
                                    'OO buffers, arbitration schemes) makes manual '
                                    'exploration time-consuming and often results '
                                    'in overdesigned solutions. Automated '
                                    'synthesis approaches aim to optimize topology '
                                    'and parameters simultaneously to minimize '
                                    'busses while meeting performance targets.\n'
                                    '\n'
                                    '- Generality versus specialization: Fully '
                                    'generic, high-connectivity buses are '
                                    'versatile but inefficient for many MPSoC '
                                    'workloads. Specialized, partial/hierarchical '
                                    "architectures tailored to the application's "
                                    'communication patterns can achieve similar or '
                                    'better throughput with much less hardware, at '
                                    'the cost of more design effort or less '
                                    'universal applicability.\n'
                                    '\n'
                                    '- Trade-offs in topology choice: '
                                    'Crossbar-like structures offer high '
                                    'throughput and parallel access but scale '
                                    'poorly in area and power; partial crossbars '
                                    'or hierarchical buses can deliver comparable '
                                    'performance for specific workloads with far '
                                    'smaller interconnect overhead, but may '
                                    'require careful workload-aware design and '
                                    'parameter tuning.\n'
                                    '\n'
                                    '- Emergence of asynchronous and modular '
                                    'design concepts: To balance timing, power, '
                                    'and routing constraints across growing '
                                    'MPSoCs, designers increasingly prefer '
                                    'modular, hierarchical, and potentially '
                                    'asynchronous approaches that decouple local '
                                    'and global communication, improving timing '
                                    'closure and scalability without relying on '
                                    'linear scaling of a single global bus.\n'
                                    '\n'
                                    'In short, the evolution from linear to '
                                    'hierarchical/asynchronous bus architectures '
                                    'is driven by the need to manage interconnect '
                                    'congestion, power, and area while preserving '
                                    'or enhancing bandwidth and timing, through '
                                    'automated, workload-aware synthesis of '
                                    'partial/topology-aware bus matrices rather '
                                    'than blindly scaling a full, uniform bus '
                                    'model.',
                              provider='exa',
                              query='What persistent engineering challenges and '
                                    'inherent trade-offs (e.g., speed vs. distance, '
                                    'power consumption vs. bandwidth, generality vs. '
                                    'specialization) have driven the evolution of '
                                    'CPU bus architectures towards hierarchical and '
                                    'asynchronous designs, rather than simply '
                                    'scaling initial linear models?',
                              intent='research',
                              priority='high',
                              fusion_score=1,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='Microprocessor system buses: A case study',
                              url='https://www.sciencedirect.com/science/article/abs/pii/S1383762198000551',
                              content='Summary:\n'
                                    '\n'
                                    'The paper analyzes seven microprocessor '
                                    'system buses (ISA, EISA, MicroChannel, VME, '
                                    'NuBus, FutureBus, PCI) with emphasis on '
                                    'modern iterations (VME64, FutureBus+, PCI) to '
                                    'illustrate design principles and tradeoffs '
                                    'shaping bus evolution. Key persistent '
                                    'engineering challenges highlighted include:\n'
                                    '\n'
                                    '- Performance vs. compatibility and '
                                    'interoperability: The bus must provide a '
                                    'stable interface across vendors while meeting '
                                    'throughput targets, requiring careful choice '
                                    'of bus parameters and design alternatives.\n'
                                    '- Speed vs. latency and distance: Memory '
                                    'speeds are outrunning CPUs, but memory burst '
                                    'latency remains a dominant factor; wider data '
                                    'paths boost bandwidth but add cost, pin '
                                    'count, reliability concerns, and complexity.\n'
                                    '- Power and heat vs. bandwidth: Increasing '
                                    'bus width and speed raises power consumption '
                                    'and thermal design challenges.\n'
                                    '- Generality vs. specialization: Buses must '
                                    'support diverse peripherals and varying I/O '
                                    'devices; software-based automatic '
                                    'configuration becomes essential as device '
                                    'complexity grows.\n'
                                    '- Hierarchical and asynchronous design '
                                    'rationale: As CPUs and memories outpace bus '
                                    'capabilities, modern designs move toward '
                                    'hierarchical, multi-layered architectures and '
                                    'asynchronous signaling to improve '
                                    'scalability, latency management, and resource '
                                    'contention, rather than simply linearly '
                                    'increasing bus speed.\n'
                                    '- Long-latency transaction handling: There '
                                    'are ongoing efforts (notably in PCI) to '
                                    'address long-latency transactions, indicating '
                                    'a shift from purely raw bandwidth to smarter '
                                    'latency-tolerant protocols and transaction '
                                    'models.\n'
                                    '- Evolution through tradeoffs: The paper '
                                    'frames evolution as a series of tradeoffs '
                                    'among throughput, compatibility, technology '
                                    'independence, configurability, and '
                                    'multiprocessor support, rather than a single '
                                    'path of faster, wider buses.\n'
                                    '\n'
                                    'In short, the movement toward hierarchical '
                                    'and asynchronous bus architectures is driven '
                                    'by the need to balance throughput, latency, '
                                    'power, configurability, and cross-vendor '
                                    'interoperability in the face of diverging '
                                    'device and memory speeds, rather than merely '
                                    'scaling up a linear, synchronous bus model.',
                              provider='exa',
                              query='What persistent engineering challenges and '
                                    'inherent trade-offs (e.g., speed vs. distance, '
                                    'power consumption vs. bandwidth, generality vs. '
                                    'specialization) have driven the evolution of '
                                    'CPU bus architectures towards hierarchical and '
                                    'asynchronous designs, rather than simply '
                                    'scaling initial linear models?',
                              intent='research',
                              priority='high',
                              fusion_score=3,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='Design Complexity In The Golden Age Of '
                                    'Semiconductors',
                              url='https://semiengineering.com/design-complexity-in-the-golden-age-of-semiconductors/',
                              content='Summary:\n'
                                    '\n'
                                    'The article examines how design complexity in '
                                    'SoCs has grown far beyond simple transistor '
                                    'scaling, driving a shift from linear, '
                                    'monolithic bus schemes to hierarchical and '
                                    'increasingly sophisticated interconnects '
                                    '(NoCs) and IP integration management. Key '
                                    'points relevant to the user’s question:\n'
                                    '\n'
                                    '- NoCs emerged to connect a growing sea of '
                                    'SIP blocks (IP blocks, CPUs, GPUs, '
                                    'accelerators) as packaging and chiplet '
                                    'concepts advanced, making simple '
                                    'point-to-point buses insufficient.\n'
                                    '- AMBA has evolved through multiple '
                                    'generations (ASB/APB → AHB → AXI → '
                                    'AXI5/ACE/LPI, etc.) to support higher '
                                    'performance, coherence, power management, '
                                    'QoS, and multi-channel interconnects. '
                                    'Complexity is measured by the expanding '
                                    'specification size (pages), reflecting richer '
                                    'features and capabilities.\n'
                                    '- The need for coherence, cache management, '
                                    'power efficiency, and quality-of-service has '
                                    'driven features like CHI, ACE extensions, and '
                                    'LPI, enabling scalable, heterogeneous systems '
                                    'beyond traditional synchronous, single-rail '
                                    'buses.\n'
                                    '- Hierarchical and modular design practices '
                                    '(NoCs, IP-XACT for design automation, and '
                                    'standardized interfaces) address the '
                                    'practical limits of scaling: routing '
                                    'complexity, timing closure, power, and '
                                    'verification in large SoCs.\n'
                                    '- The industry response to rising SIP block '
                                    'counts and integration challenges includes '
                                    'design automation standards (IP-XACT, VSI '
                                    'Alliance, SPIRIT) and multi-chip/CHIs for '
                                    'inter-chip coherence, illustrating a move '
                                    'from linear scaling to architecture that '
                                    'emphasizes locality, specialization where '
                                    'appropriate, and managed heterogeneity.\n'
                                    '\n'
                                    'In short, persistent engineering challenges '
                                    'driving the shift include: scalability of '
                                    'interconnects as SIP counts grow, the need '
                                    'for cache coherence and power-aware '
                                    'protocols, performance and QoS demands, and '
                                    'the complexity of integrating diverse IP '
                                    'blocks—pushing architectures toward '
                                    'hierarchical, asynchronous-capable, and '
                                    'protocol-rich NoCs rather than relying on '
                                    'simple linear, synchronous buses.',
                              provider='exa',
                              query='What persistent engineering challenges and '
                                    'inherent trade-offs (e.g., speed vs. distance, '
                                    'power consumption vs. bandwidth, generality vs. '
                                    'specialization) have driven the evolution of '
                                    'CPU bus architectures towards hierarchical and '
                                    'asynchronous designs, rather than simply '
                                    'scaling initial linear models?',
                              intent='research',
                              priority='high',
                              fusion_score=1,
                              rerank_score=0.0,
                              score=None,
                              published_date='2023-08-24T07:06:41.000Z'),
      UnifiedRetrievalResult(title='Buses',
                              url='https://users.ece.cmu.edu/~koopman/ece548/handouts/18bus.pdf',
                              content='Summary:\n'
                                    'The material outlines how computer buses '
                                    'evolved from ad-hoc point-to-point '
                                    'connections to structured interconnects, '
                                    'shaping key architecture concerns. Early '
                                    'designs used direct wires between subsystems, '
                                    'which offered high potential bandwidth but '
                                    'with prohibitive cost, scale, and '
                                    'expandability issues. To address these, '
                                    'designers moved to regular interconnection '
                                    'structures (e.g., crossbars, bus hierarchies) '
                                    'that trade off cost, bandwidth, and latency.\n'
                                    '\n'
                                    'Core implications for modern architecture:\n'
                                    '- Cache coherence and memory hierarchy: Buses '
                                    'and interconnects centralize or distribute '
                                    'traffic between CPU, caches, memory, and I/O. '
                                    'As bandwidth demands rose, architectures '
                                    'adopted separated or multiple buses (e.g., '
                                    'backside cache bus, memory vs I/O buses, PCI '
                                    'bridges) to reduce contention and support '
                                    'coherence protocols. Crossbar-like '
                                    'interconnects and scalable architectures '
                                    'enable coherent, high-speed access to memory '
                                    'across multiple cores and memory banks.\n'
                                    '- Memory management: Bus design influences '
                                    'how memory controllers, DMA, and I/O devices '
                                    'share the memory subsystem. DMA and '
                                    'cycle-stealing mechanisms show how external '
                                    'devices can access memory without CPU '
                                    'intervention, affecting latency, bandwidth, '
                                    'and memory ordering behavior.\n'
                                    '- System-level performance and '
                                    'programmability: Increasing bus width, moving '
                                    'from parallel to (and incorporating) serial '
                                    'interconnects, and introducing '
                                    'bridges/expansion buses improve scalability, '
                                    'expandability, and bandwidth utilization. '
                                    'This reduces bottlenecks for CPUs, '
                                    'accelerators, and peripherals, enabling more '
                                    'complex memory hierarchies and unified '
                                    'address spaces, which in turn simplifies or '
                                    'complicates programming models depending on '
                                    'the coherence and ordering guarantees '
                                    'provided by the interconnect.\n'
                                    '\n'
                                    'In short, evolving CPU bus complexity and '
                                    'abstractions have driven coherent memory '
                                    'access, scalable and flexible memory '
                                    'hierarchies, and higher aggregate system '
                                    'performance, while also shaping the '
                                    'programmability model through coherence, '
                                    'ordering, and DMA-enabled data movement.',
                              provider='exa',
                              query='Beyond merely facilitating data movement, how '
                                    'has the evolving complexity and abstraction of '
                                    'CPU bus systems profoundly influenced critical '
                                    'aspects of modern computer architecture, '
                                    'including cache coherence, memory management, '
                                    'and the overall system-level performance and '
                                    'programmability?',
                              intent='research',
                              priority='high',
                              fusion_score=2,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='Interconnections in Multi-Core Architectures:  '
                                    'Understanding Mechanisms, Overheads and Scaling',
                              url='https://dl.acm.org/doi/10.1145/1080695.1070004',
                              content='Summary:\n'
                                    '\n'
                                    'This paper argues that on-chip interconnects '
                                    'are a first-order design choice that '
                                    'profoundly shapes modern multicore '
                                    'architecture. Key takeaways aligned with your '
                                    'query:\n'
                                    '\n'
                                    '- Interconnects influence area, power, and '
                                    'performance budgets far beyond data movement, '
                                    'often consuming a large fraction of die area '
                                    'and dynamic power. Consequently, interconnect '
                                    'design cannot be decoupled from other '
                                    'subsystems.\n'
                                    '- Co-design is essential: treating the '
                                    'interconnect in isolation leads to suboptimal '
                                    'multi-core designs. Bandwidth increases can '
                                    'paradoxically constrain core counts and cache '
                                    'sizes due to area and power trade-offs, and '
                                    'can worsen performance if not matched with '
                                    'coherence and memory hierarchy redesigns.\n'
                                    '- Cache coherence and memory hierarchy: the '
                                    'interconnect architecture directly impacts '
                                    'coherence traffic and the viability of cache '
                                    'organizations (e.g., shared L2 caches vs. '
                                    'private caches). Crossbars and coherence '
                                    'directories introduce substantial overheads '
                                    'that must be weighed against potential '
                                    'performance gains.\n'
                                    '- Hierarchical and proximity-aware designs: '
                                    'hierarchical bus structures and '
                                    'proximity-aware coherence mechanisms can '
                                    'mitigate some scalability and coherence '
                                    'overheads, suggesting that scalable '
                                    'performance emerges from co-architecting '
                                    'coherence protocols, interconnect topology, '
                                    'and caching strategies.\n'
                                    '- System-level performance and '
                                    'programmability: effective interconnect '
                                    'design shapes how memory is accessed, how '
                                    'coherency is maintained across cores, and how '
                                    'easily the system can be programmed to '
                                    'exploit locality and parallelism. The '
                                    'abstraction of the interconnect as a '
                                    'separable unit can hinder performance and '
                                    'simplicity if not complemented by integrated '
                                    'design of memory hierarchy, coherence, and '
                                    'interconnect topology.\n'
                                    '\n'
                                    'In short, the evolution of CPU bus systems '
                                    'has driven a shift toward tightly integrated, '
                                    'co-optimized interconnect and memory '
                                    'hierarchies, where coherence protocols, cache '
                                    'organization, and memory management '
                                    'techniques are designed in concert with the '
                                    'interconnect to achieve scalable performance '
                                    'and programmable efficiency.',
                              provider='exa',
                              query='Beyond merely facilitating data movement, how '
                                    'has the evolving complexity and abstraction of '
                                    'CPU bus systems profoundly influenced critical '
                                    'aspects of modern computer architecture, '
                                    'including cache coherence, memory management, '
                                    'and the overall system-level performance and '
                                    'programmability?',
                              intent='research',
                              priority='high',
                              fusion_score=3,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='CPU Buses: The Hidden Highways Powering Modern '
                                    'Processors - Digitalidiom.co.uk',
                              url='https://www.digitalidiom.co.uk/cpu-buses/',
                              content='Summary:\n'
                                    'The article traces how CPU buses have evolved '
                                    'from wide, shared paths to modular, '
                                    'point-to-point fabrics, profoundly shaping '
                                    'modern architecture. Key impacts:\n'
                                    '\n'
                                    '- Cache coherence: Interconnects and '
                                    'coherence protocols enable fast, consistent '
                                    'data views across cores and sockets, reducing '
                                    'stalls and keeping caches synchronized in '
                                    'multi-core and multi-processor systems.\n'
                                    '- Memory management: Integration of memory '
                                    'controllers on CPUs and wider, high-speed '
                                    'memory channels reshaped memory traffic, '
                                    'latency, and bandwidth. Narrower or more '
                                    'predictable data paths and advanced memory '
                                    'protocols improved reliability and '
                                    'performance across channels.\n'
                                    '- System-level performance: Moving from '
                                    'single, monolithic buses to scalable '
                                    'interconnects lowers contention, tail '
                                    'latency, and power per bit moved. This '
                                    'enables higher aggregate bandwidth to memory, '
                                    'I/O, and accelerators, and better scalability '
                                    'as cores, sockets, and devices proliferate.\n'
                                    '- Programmability and abstraction: Modern '
                                    'interconnects expose abstractions that '
                                    'balance latency, bandwidth, and coherence, '
                                    'influencing software design—memory access '
                                    'patterns, NUMA awareness, and cache-friendly '
                                    'algorithms—while hardware optimizations '
                                    '(topologies, protocols, on-die links) drive '
                                    'predictable performance.\n'
                                    '- Overall architecture strategy: The shift to '
                                    'on-die interconnects and modular fabrics '
                                    'decouples performance goals (latency vs. '
                                    'bandwidth) from old monolithic buses, '
                                    'enabling tailored designs for core-to-core, '
                                    'core-to-memory, and I/O paths, and driving '
                                    'system-level efficiency, scalability, and '
                                    'programmability.\n'
                                    '\n'
                                    'In short, evolving CPU bus architectures have '
                                    'moved performance-critical responsibilities '
                                    '(coherence, memory access efficiency, and '
                                    'cross-component communication) from rigid, '
                                    'single paths to sophisticated, scalable '
                                    'interconnects, directly shaping how software '
                                    'runs efficiently, predictably, and at scale.',
                              provider='exa',
                              query='Beyond merely facilitating data movement, how '
                                    'has the evolving complexity and abstraction of '
                                    'CPU bus systems profoundly influenced critical '
                                    'aspects of modern computer architecture, '
                                    'including cache coherence, memory management, '
                                    'and the overall system-level performance and '
                                    'programmability?',
                              intent='research',
                              priority='high',
                              fusion_score=4,
                              rerank_score=0.0,
                              score=None,
                              published_date='2025-10-01T11:24:08.000Z'),
      UnifiedRetrievalResult(title='',
                              url='https://pages.cs.wisc.edu/~markhill/papers/primer2020_2nd_edition.pdf',
                              content='The primer explains how shared memory systems '
                                    'and their memory consistency models shape '
                                    'modern computer architecture. It covers:\n'
                                    '\n'
                                    '- How CPUs with shared address spaces rely on '
                                    'memory consistency models to define correct '
                                    'inter-thread memory behavior for loads and '
                                    'stores.\n'
                                    '- The role of cache coherence protocols in '
                                    'keeping multiple cached data copies '
                                    'consistent across cores.\n'
                                    '- How these mechanisms interact to impact '
                                    'performance, memory management, and '
                                    'programmability at the system level.\n'
                                    '- Evolution across editions, including '
                                    'updates for non-CPU accelerators (GPUs) and '
                                    'formal tools, reflecting growing complexity '
                                    'in coherence and consistency in real '
                                    'hardware.\n'
                                    '- Practical examples and case studies across '
                                    'real-world systems, illustrating the '
                                    'trade-offs and design choices that affect '
                                    'system throughput, latency, and ease of '
                                    'programming.\n'
                                    '\n'
                                    'If you’re exploring how increasing '
                                    'abstraction and heterogeneity in CPU bus '
                                    'systems affect cache coherence, memory '
                                    'management, and end-to-end performance, this '
                                    'primer provides foundational concepts, '
                                    'architectures, and concrete examples from '
                                    'current systems.',
                              provider='exa',
                              query='Beyond merely facilitating data movement, how '
                                    'has the evolving complexity and abstraction of '
                                    'CPU bus systems profoundly influenced critical '
                                    'aspects of modern computer architecture, '
                                    'including cache coherence, memory management, '
                                    'and the overall system-level performance and '
                                    'programmability?',
                              intent='research',
                              priority='high',
                              fusion_score=1,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='The northbridge that disappeared: how '
                                    'integration rewired PCs – cr0x.net',
                              url='https://cr0x.net/en/northbridge-disappeared-pc-integration/',
                              content='Summary:\n'
                                    'The evolution from a distinct northbridge to '
                                    'integrated CPU memory controllers and on-die '
                                    'interconnects has reshaped core system '
                                    'architecture in several deep ways. By moving '
                                    'memory control, high-speed I/O, and even '
                                    'early graphics onto the CPU die or tightly '
                                    'coupled fabrics, latency reduces and power '
                                    'use drops, but responsibility for timing, '
                                    'bandwidth allocation, and coherence shifts '
                                    'away from discrete chipsets to the CPU and '
                                    'its on-die interconnects. This integration '
                                    'changes:\n'
                                    '\n'
                                    '- Cache coherence: coherence management '
                                    'increasingly sits inside the CPU package and '
                                    'is propagated over on-die rings/meshes, '
                                    'reducing synchronization overhead and '
                                    'centralizing coherence policies, but also '
                                    'concentrating complexity within the '
                                    'processor’s fabric.\n'
                                    '- Memory management: memory controllers '
                                    'become on-die (or tightly integrated) '
                                    'components, enabling smarter, more uniform '
                                    'memory timing, rank/channel arbitration, and '
                                    'improved scheduling. This tight coupling '
                                    'improves latency and predictability for many '
                                    'workloads yet raises stakes for CPU-centric '
                                    'failures and microarchitectural bugs.\n'
                                    '- System-level performance: shorter '
                                    'interconnects, fewer external hops, and '
                                    'integrated PCIe lanes reduce latency and '
                                    'power per transaction, but introduce '
                                    'competition for bandwidth across CPU cores, '
                                    'GPU, storage, and I/O, often constrained by '
                                    'shared uplinks (e.g., DMI or similar). This '
                                    'shifts bottlenecks from motherboard chipset '
                                    'limitations to CPU memory/interconnect '
                                    'bandwidth and firmware/microcode policies.\n'
                                    '- Programmability and debugging: developers '
                                    'increasingly reason about performance and '
                                    'latency in terms of on-die fabrics, memory '
                                    'channels, and PCIe root complexes rather than '
                                    'discrete chipset behavior. Troubleshooting '
                                    'now involves microcode, firmware, and '
                                    'interconnect policies rather than a '
                                    'standalone northbridge.\n'
                                    '\n'
                                    'In short, higher integration rewired where '
                                    'latency and bandwidth contention occur, '
                                    'centralized more in the CPU and its internal '
                                    'networks, while the visible chipset role '
                                    'shrinks to I/O routing. This yields better '
                                    'efficiency and coherence within the CPU, but '
                                    'pushes systemic performance and debugging '
                                    'challenges into the realm of on-die '
                                    'architectures, firmware, and fabric-level '
                                    'policies.',
                              provider='exa',
                              query='Beyond merely facilitating data movement, how '
                                    'has the evolving complexity and abstraction of '
                                    'CPU bus systems profoundly influenced critical '
                                    'aspects of modern computer architecture, '
                                    'including cache coherence, memory management, '
                                    'and the overall system-level performance and '
                                    'programmability?',
                              intent='research',
                              priority='high',
                              fusion_score=2,
                              rerank_score=0.0,
                              score=None,
                              published_date='2026-01-10T17:53:39.000Z'),
      UnifiedRetrievalResult(title='',
                              url='https://goens.org/publications/pldi26.pdf',
                              content='Summary:\n'
                                    'The document presents a formal framework for '
                                    'reasoning about heterogeneous, '
                                    'memory-coherence systems where components (CR '
                                    'CPUs, GPUs, accelerators) use different '
                                    'memory consistency models (MCMs). It argues '
                                    'that global coherence interconnects (e.g., '
                                    'CXL, CHI) alone do not solve the complexity; '
                                    'designers must still implement interface '
                                    'logic (shims) to fuse local device protocols '
                                    'with the global interconnect. The core '
                                    'contribution is a formal abstraction for '
                                    'diverse coherence protocols that combines '
                                    'abstract states, consistency labels, and '
                                    'linearization points, enabling compositional '
                                    'reasoning about protocol composition. The '
                                    'authors prove that if each device protocol '
                                    'satisfies the abstraction’s axioms and the '
                                    'global interconnect enforces an SWMR '
                                    '(single-writer/multiple-reader) invariant, '
                                    'then their composition enforces Compound '
                                    'Memory Consistency Models (CMCM). This '
                                    'provides a compositional verification '
                                    'framework that reduces the global problem to '
                                    'verifying individual protocols against the '
                                    'axioms and the SWMR property of the global '
                                    'interconnect. The work is validated against '
                                    'industrial-strength protocols (e.g., CXL) and '
                                    'academic models, and is framed within '
                                    'heterogeneous systems that fuse SWMR-based '
                                    'CPU/GPU clusters via a global SWMR-enforcing '
                                    'fabric.',
                              provider='exa',
                              query='Beyond merely facilitating data movement, how '
                                    'has the evolving complexity and abstraction of '
                                    'CPU bus systems profoundly influenced critical '
                                    'aspects of modern computer architecture, '
                                    'including cache coherence, memory management, '
                                    'and the overall system-level performance and '
                                    'programmability?',
                              intent='research',
                              priority='high',
                              fusion_score=1,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='Microprocessor system buses: A case study',
                              url='https://www.sciencedirect.com/science/article/abs/pii/S1383762198000551',
                              content='Summary:\n'
                                    '\n'
                                    'The paper reviews seven microprocessor system '
                                    'buses (ISA, EISA, MicroChannel, NuBus, '
                                    'FutureBus, VME, PCI) with emphasis on modern '
                                    'successors (VME64, FutureBus+, PCI). It '
                                    'discusses how a system bus serves as a '
                                    'standard, interoperable interface across '
                                    'vendors and how its design choices shape '
                                    'overall system performance. Key themes '
                                    'relevant to your query include:\n'
                                    '\n'
                                    '- Influence on performance and latency: Bus '
                                    'bandwidth, transfer parameters, and latency '
                                    'critically limit system performance. As CPUs '
                                    'outpace memory, memory latency remains a '
                                    'dominant factor in bus utilization, driving '
                                    'design tradeoffs between speed, interleaving, '
                                    'and burst capabilities.\n'
                                    '\n'
                                    '- Complexity and abstraction: Increasing I/O '
                                    'device sophistication necessitates '
                                    'software-based automatic configuration and '
                                    'richer bus protocols, improving '
                                    'programmability and system integration while '
                                    'raising architectural complexity.\n'
                                    '\n'
                                    '- Cache coherence and multiprocessor support: '
                                    'Bus arbitration and protocol choices are '
                                    'central to maintaining coherence and '
                                    'coordinating shared resources in '
                                    'multiprocessing environments, affecting '
                                    'throughput and scalability.\n'
                                    '\n'
                                    '- Memory management and addressing: Bus '
                                    'width, address signaling, and the ability to '
                                    'extend addressing (e.g., split address '
                                    'phases) influence memory virtualization, '
                                    'addressing range, and capable memory '
                                    'subsystems, impacting both performance and '
                                    'programming models.\n'
                                    '\n'
                                    '- Design tradeoffs and evolution: The '
                                    'evolution from ISA-era protocols to PCI and '
                                    'beyond shows how compatibility, '
                                    'interoperability, technology independence, '
                                    'and throughput requirements drive '
                                    'architectural changes, including asynchronous '
                                    'vs. synchronous designs and Plug-and-Pay '
                                    'concepts.\n'
                                    '\n'
                                    'Overall, the paper frames the system bus not '
                                    'merely as a data conduit but as a core '
                                    'architectural element that constrains or '
                                    'enables cache coherence strategies, memory '
                                    'management mechanisms, and system-level '
                                    'performance, while shaping programmability '
                                    'through configuration, interoperability, and '
                                    'evolving protocol standards.',
                              provider='exa',
                              query='Beyond merely facilitating data movement, how '
                                    'has the evolving complexity and abstraction of '
                                    'CPU bus systems profoundly influenced critical '
                                    'aspects of modern computer architecture, '
                                    'including cache coherence, memory management, '
                                    'and the overall system-level performance and '
                                    'programmability?',
                              intent='research',
                              priority='high',
                              fusion_score=3,
                              rerank_score=0.0,
                              score=None,
                              published_date=None),
      UnifiedRetrievalResult(title='NoC Coherency Challenges Balloon With AI SoCs '
                                    'And Chiplets',
                              url='https://semiengineering.com/noc-coherency-challenges-balloon-with-ai-socs-and-chiplets/',
                              content='Summary:\n'
                                    'The article discusses how growing complexity '
                                    'in NoC (network-on-chip) designs, chiplets, '
                                    'and AI-enabled SoCs is reshaping core '
                                    'architectural concerns beyond simple data '
                                    'movement. Key points:\n'
                                    '\n'
                                    '- Cache coherence vs. non-coherence: '
                                    'Maintaining a coherent memory view across '
                                    'multiple CPU cores is significantly more '
                                    'complex and power- and area-intensive than '
                                    'non-coherent I/O paths. Designers often '
                                    'isolate coherence to memory/CPU boundaries '
                                    'and keep other domains non-coherent to reduce '
                                    'overhead.\n'
                                    '- Memory management implications: Coherent '
                                    'interfaces must manage memory traffic and '
                                    'consistency across processors, while '
                                    'non-coherent domains rely on simpler '
                                    'read/write protocols. Distinct coherent and '
                                    'non-coherent networks complicate memory '
                                    'hierarchy design and require careful '
                                    'partitioning of memory access '
                                    'responsibilities.\n'
                                    '- Chiplet and multi-die implications: '
                                    'Multi-chiplet and 3D/stacked architectures '
                                    'demand robust management of both coherent and '
                                    'non-coherent NoCs. The central system chiplet '
                                    'typically must support dual interfaces — '
                                    'coherent with CPUs and non-coherent to AI '
                                    'accelerators — to balance memory control with '
                                    'accelerator data movement.\n'
                                    '- Programmability and system discovery: As '
                                    'chiplets and packages scale, boot-time '
                                    'discovery, routing configuration, and runtime '
                                    'programmability become critical. Systems need '
                                    'management agents to map processes, route '
                                    'traffic, and reconfigure networks as chiplets '
                                    'wake and learn their identities within a '
                                    'package.\n'
                                    '- Performance and design trade-offs: '
                                    'Designers are increasingly partitioning '
                                    'memory and signaling domains (e.g., creating '
                                    '“even/odd” memory networks) to maximize data '
                                    'throughput while managing coherence overhead, '
                                    'illustrating how data movement abstractions '
                                    'evolve into broader system-level performance '
                                    'considerations.\n'
                                    '- Overall impact: The evolving abstractions '
                                    'around CPU bus systems—especially regarding '
                                    'cache coherence, memory management, and '
                                    'inter-chiplet communication—drive changes in '
                                    'programmability, discovery protocols, and '
                                    'higher-level system design to sustain '
                                    'performance in heterogeneous, multi-die '
                                    'environments.',
                              provider='exa',
                              query='Beyond merely facilitating data movement, how '
                                    'has the evolving complexity and abstraction of '
                                    'CPU bus systems profoundly influenced critical '
                                    'aspects of modern computer architecture, '
                                    'including cache coherence, memory management, '
                                    'and the overall system-level performance and '
                                    'programmability?',
                              intent='research',
                              priority='high',
                              fusion_score=1,
                              rerank_score=0.0,
                              score=None,
                              published_date='2026-04-30T00:00:00.000Z')]
    
      
      pprint(response)


'''