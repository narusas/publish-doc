# AWS 기초 튜토리얼 — 사실 검증 기록

- 날짜: 2026-08-15
- 대상 문서: `aws_basics.html` (설계: `docs/superpowers/specs/2026-08-15-aws-basics-tutorial-design.md`)
- 방법: AWS 공식 문서 원문을 직접 받아 인용. 요약본이 아니라 인용문을 근거로 삼는다.

**옮겨 쓸 때의 규칙** — `2026-08-14-known-issues.md` §10에서 옮겨 온다.

1. 아래 표·요약과 인용문이 어긋나면 **인용문을 믿는다.**
2. 여기에 없는 사실은 **쓰지 말고 비워 둔 채 보고한다.** 완화해서 뭉개지 않는다.
3. 요금 숫자는 **리전마다 다르다.** 아래 값은 공식 페이지에 적힌 그대로이고, 어느 리전 표인지
   명시돼 있지 않았다. 본문에서는 절대값보다 **무엇이 시간당인가**를 축으로 쓴다.

---

## V1 · 퍼블릭 IPv4는 stop하면 바뀐다 — 확인됨

출처: [Amazon EC2 instance IP addressing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html)

> We release the public IP address when the instance is stopped, hibernated, or terminated.
> We assign a new public IP address when you start your stopped or hibernated instance.

> A public IP address is assigned to your instance from Amazon's pool of public IPv4 addresses,
> and is not associated with your AWS account.

사설 IP는 반대다.

> A private IPv4 address, regardless of whether it is a primary or secondary address, remains
> associated with the network interface when the instance is stopped and started, or hibernated
> and started, and is released when the instance is terminated.

**주의**: 이 페이지는 재부팅(reboot)을 해제 사유 **목록에 넣지 않았다.** 목록에 없다는 사실까지가
확인된 것이고, "재부팅하면 유지된다"는 문장은 이 페이지에서 직접 인용되지 않는다. 7장에서
재부팅을 다룰 때는 인스턴스 스토어 쪽 표(V8)를 근거로 쓴다 — 거기에는 reboot 행이 있다.

부수 확인 — 퍼블릭 IP가 해제돼도 새로 안 주는 두 경우:

> If we release the public IP address of your instance and it has a secondary network interface,
> we do not assign a new public IP address.

---

## V2 · 퍼블릭 IPv4는 붙어 있어도 과금된다 — 확인됨

출처 ①: [Amazon EC2 instance IP addressing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html)

> AWS charges for all public IPv4 addresses, including public IPv4 addresses associated with
> running instances and Elastic IP addresses.

출처 ②: [Amazon VPC Pricing](https://aws.amazon.com/vpc/pricing/) — 두 줄이 **같은 값**이다.

> Hourly charge for In-use Public IPv4 Address $0.005
> Hourly charge for Idle Public IPv4 Address $0.005

출처 ③: [New – AWS Public IPv4 Address Charge + Public IP Insights](https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights/) ·
[AWS Free Tier now includes 750 hours of free Public IPv4 addresses](https://aws.amazon.com/about-aws/whats-new/2024/02/aws-free-tier-750-hours-free-public-ipv4-addresses/)

- 시행: **2024년 2월 1일**
- 붙어 있든 놀고 있든 시간당 $0.005
- EC2 프리 티어에 월 750시간이 첫 12개월간 포함된다
- BYOIP로 가져온 주소는 과금되지 않는다
- EC2뿐 아니라 RDS·EKS 노드 등 퍼블릭 IPv4를 붙일 수 있는 모든 서비스에 적용된다

**12장에 쓸 것**: "안 쓰는 EIP만 돈이 나간다"는 낡은 상식이다. 지금은 **쓰고 있어도 같은 값**이 나간다.
값이 같으므로 이 문서는 "붙였다/놀린다"가 아니라 **"몇 개나 갖고 있나"**를 축으로 쓴다.

---

## V3 · `DeleteOnTermination` 기본값 — **설계 문서가 틀렸다. 수정 필요**

출처: [Preserve data when an instance is terminated](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/preserving-volumes-on-termination.html)

설계 §5 6장에 "루트 볼륨과 추가 볼륨의 기본값이 갈린다"고 적었는데, 갈리는 축이 **둘이 아니라 셋**이다 —
볼륨 종류 · 언제 붙였나 · **콘솔이냐 CLI냐**.

| Volume type | Attached when | Method for attaching | Default behavior on instance termination |
| --- | --- | --- | --- |
| Root volume | At launch | Console or CLI | **Delete** |
| Root volume | After launch | Console or CLI | Preserve |
| Data volume | At launch | Console | Preserve |
| Data volume | At launch | **CLI** | **Delete** |
| Data volume | After launch | Console and CLI | Preserve |

같은 "시작할 때 붙인 데이터 볼륨"인데 **콘솔은 남기고 CLI는 지운다.** 6장이 노릴 자리가 여기다.
13장("콘솔과 CLI는 같은 문")과 정면으로 부딪히는 것처럼 보이지만 모순이 아니다 — 문은 하나이고,
**콘솔이 대신 채워 넣는 기본값이 다를 뿐**이다. 두 장을 잇는 데 쓴다.

> **No** (console) / `false` (CLI) – The volume is preserved when the instance is terminated.
> Preserved volumes continue to incur charges.

또 하나:

> The default value at launch for an EBS volume is determined by the `DeleteOnTermination`
> attribute set on the AMI.

즉 최종 결정권은 AMI에 있다. **"기본값은 X다"라고 단정하지 말 것.**

---

## V4 · NAT Gateway 과금 축 — 확인됨

출처 ①: [Amazon VPC Pricing](https://aws.amazon.com/vpc/pricing/) — 시간당 $0.045, 처리 GB당 $0.045.
트래픽의 출발지·목적지와 무관하게 지나간 양으로 받는다.

출처 ②: [Amazon EC2 instance IP addressing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html) —
같은 값이 EC2 사용자 안내서의 계산식에도 그대로 나온다. 두 페이지가 독립적으로 일치한다.

> `NAT gateway per hour = $0.045 * 730 hours in a month * Number of Availability Zones the NAT gateways are in`
> `NAT gateway public IPs = $0.005 * 730 hours in a month * Number of IPs associated with your NAT gateways`
> `NAT gateway transfer = $0.045 * Number of GBs that will go through the NAT gateway in a month`

**9장·12장에 쓸 것**: NAT Gateway는 **AZ마다 하나씩** 두므로 시간당 요금이 AZ 수만큼 곱해진다.
그리고 NAT Gateway 자신도 퍼블릭 IP를 쥐고 있어서 V2의 $0.005가 **또 붙는다.** 요금이 세 겹이다.

---

## V5 · S3 버킷 이름은 "전 세계"가 아니라 "파티션 안에서" 유일하다 — 확인됨

출처: [General purpose bucket naming rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html)

> General purpose buckets exist in a global namespace, which means that each bucket name must be
> unique across all AWS accounts in all the AWS Regions **within a partition**. A partition is a
> grouping of Regions. AWS currently has four partitions: `aws` (Standard Regions), `aws-cn`
> (China Regions), `aws-us-gov` (AWS GovCloud (US)), and `aws-eusc` (European Sovereign Cloud).

**함께 확인된 것 — 계정 리전 네임스페이스(account regional namespace).** 전역 네임스페이스 말고
계정 전용 네임스페이스에 버킷을 만들 수 있다. 이름 규칙은 `{prefix}-{계정ID}-{리전}-an`이다.

> New general purpose buckets created in your account regional namespace are unique to your
> account and can never be re-created by another account.

8장에서 "이름을 남에게 뺏긴다"를 다룬 뒤 해법으로 한 줄 붙일 수 있다. **필수는 아니다.**

---

## V6 · `ap-northeast-2a`는 계정마다 다른 건물이다 — 확인됨

출처: [Availability Zone IDs for your AWS resources](https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html)

> AWS maps the physical Availability Zones *randomly* to the Availability Zone names for each AWS
> account. ... As a result, the Availability Zone `us-east-1a` for *your* AWS account might not
> represent the same physical location as `us-east-1a` for a different AWS account.

> An AZ ID is a unique and consistent identifier for an Availability Zone across all AWS accounts.
> For example, `use1-az1` is an AZ ID for an Availability Zone in the `us-east-1` Region and it
> represents the same physical location in every AWS account.

**섞은 이유까지 적혀 있다.**

> This approach helps to distribute resources across the Availability Zones in an AWS Region,
> instead of resources likely being concentrated in Availability Zone "a" for each Region.

**3장 데모에 그대로 쓸 실제 출력** — 공식 문서의 `describe-availability-zones` 예시다.
`a`가 `az1`이 아니라는 것이 눈으로 보인다.

| ZoneName | ZoneId |
| --- | --- |
| us-west-2a | usw2-az2 |
| us-west-2b | usw2-az1 |
| us-west-2c | usw2-az3 |
| us-west-2d | usw2-az4 |

---

## V7 · ALB는 서브넷 둘, NLB는 하나 — 확인됨. **비대칭이다**

출처 ①: [Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html)

> **You must select at least two Availability Zone subnets.** The following restrictions apply:
> Each subnet must be from a different Availability Zone.

> verify that each Availability Zone subnet for your load balancer has a CIDR block with at least
> a `/27` bitmask (for example, `10.0.0.0/27`) and at least eight free IP addresses per subnet.

출처 ②: [Create a Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-network-load-balancer.html)

> For **Availability Zones and subnets**, **select at least one Availability Zone**, and select
> one subnet per zone.

**9장에 쓸 것**: 3장(AZ)과 7장(ENI는 서브넷에 갇힌다)이 여기서 값을 한다. 로드밸런서는 AZ마다
ENI를 하나씩 만들기 때문에 서브넷을 요구하는 것이다.

> Elastic Load Balancing creates network interfaces in the subnets where you configured your
> load balancer. ... They have the description "ENI reserved by ELB for subnet".

**ALB vs NLB의 진짜 갈림길 하나 더 — 고정 IP.** NLB는 AZ마다 EIP를 지정할 수 있다.

> When creating an internet-facing Network Load Balancer, you can choose to specify an Elastic IP
> address for each Availability Zone. Elastic IP addresses provide your Network Load Balancer with
> static IP addresses.

ALB는 그럴 수 없고, 주소를 서비스가 쥐고 있다가 회수한다.

> While these IPs are visible in your account, they remain fully managed by the Application Load
> Balancer service and cannot be modified or released.

"방화벽에 IP를 등록해야 한다"가 NLB를 고르는 실제 이유가 되는 자리다.

---

## V8 · 인스턴스 스토어는 재부팅에서만 살아남는다 — 확인됨

출처: [Data persistence for Amazon EC2 instance store volumes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-lifetime.html)

> The data on an instance store volume persists even if the instance is rebooted. However, the
> data does not persist if the instance is stopped, hibernated, or terminated. When the instance
> is stopped, hibernated, or terminated, every block of the instance store volume is
> cryptographically erased.

| Event | What happens to your data? |
| --- | --- |
| The instance is rebooted | The data persists |
| The instance is stopped | The data does not persist |
| The instance is hibernated | The data does not persist |
| The instance is terminated | The data does not persist |
| **The instance type is changed** | **The data does not persist** |
| A shutdown is initiated (OS) | The data does not persist |
| A restart is initiated (OS) | The data persists |
| The underlying disk fails | The data on the failed disk does not persist |
| Power failure | The data persists upon reboot |

**5장에 쓸 것**: OS에서 `reboot`을 치면 살고 `shutdown`을 치면 죽는다. 같은 터미널에서 한 글자
차이로 갈린다. 그리고 붙였다 뗄 수도 없다.

> Instance store volumes are attached only at instance launch. You can't attach instance store
> volumes after launch. You can't detach an instance store volume from one instance and attach it
> to a different instance.

이것이 6장 EBS와의 대비축이다 — EBS는 붙였다 뗄 수 있고, 인스턴스 스토어는 못 한다.

---

## V9 · Lambda 한계 — 확인됨. **단, "15분이 최대"는 이제 조건부다**

출처: [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)

| 항목 | 값 |
| --- | --- |
| Function timeout | 900 seconds (15 minutes) |
| Function memory allocation | 128 MB to 10,240 MB, in 1-MB increments |
| 배포 패키지 (.zip) | 50 MB (압축, API·SDK 업로드) / 250 MB (압축 해제, 레이어 포함) |
| 컨테이너 이미지 | 10 GB (압축 해제 최대 이미지 크기) |
| Concurrent executions | 1,000 (기본, 증액 가능) |
| Invocation payload | 동기 요청·응답 각 6 MB / 비동기 1 MB |

> At 1,769 MB, a function has the equivalent of one vCPU.

**주의 — 같은 페이지에 `Lambda MicroVMs`라는 별개 항목이 있고 최대 실행 시간이 8시간(28,800초)이다.**
따라서 **"Lambda는 15분이 최대다"라고 단정하면 틀린다.** 11장에서는 "Lambda **함수**의 타임아웃은
900초"로 대상을 좁혀 쓴다. MicroVM은 이 문서의 범위 밖이므로 언급하지 않는다.

> New AWS accounts have reduced concurrency and memory quotas for Lambda Functions and Lambda
> MicroVMs. AWS raises these quotas automatically based on your usage.

신규 계정은 위 기본값보다 낮게 시작한다. 이것도 "기본값은 X다"를 단정하지 못하게 하는 조건이다.

---

## V10 · RDS가 끝내 내주지 않는 것 — 확인됨

출처: [Amazon RDS Custom](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-custom.html)

> **To deliver a managed service experience, Amazon RDS doesn't let you access the underlying
> host. Amazon RDS also restricts access to some procedures and objects that require high-level
> privileges.**

10장 데모의 뼈대가 될 표. 출처: [What is Amazon RDS?](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)
(같은 표가 RDS Custom 페이지에도 실려 있다 — 두 페이지가 일치한다.)

| Feature | On-premises | Amazon EC2 | Amazon RDS |
| --- | --- | --- | --- |
| Application optimization | Customer | Customer | Customer |
| Scaling | Customer | Customer | AWS |
| High availability | Customer | Customer | AWS |
| Database backups | Customer | Customer | AWS |
| Database software patching | Customer | Customer | AWS |
| Database software install | Customer | Customer | AWS |
| Operating system (OS) patching | Customer | Customer | AWS |
| OS installation | Customer | Customer | AWS |
| Server maintenance | Customer | AWS | AWS |
| Hardware lifecycle | Customer | AWS | AWS |
| Power, network, and cooling | Customer | AWS | AWS |

**표를 그대로 쓰면 안 되는 이유가 표 자체에 있다.** 열한 줄 중 맨 윗줄만 세 열이 전부 `Customer`다.
AWS가 아무리 가져가도 **쿼리는 끝까지 내 것**이라는 이야기이고, 공식 문서도 따로 못을 박는다.

> You are responsible for query tuning ... Monitoring and tuning are highly individualized
> processes that you own for your RDS databases.

RDS Custom은 "OS 접근이 필요하면 이쪽"이라는 **탈출구**로만 한 줄 언급한다. 이 문서의 범위 밖이다.

---

## V11 · ARN에서 칸이 비는 것은 정상이다 — 확인됨

출처: [Identify AWS resources with Amazon Resource Names (ARNs)](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html)

> Be aware that the ARNs for some resources omit the Region, the account ID, or both the Region
> and the account ID.

```
arn:partition:service:region:account-id:resource-id
arn:partition:service:region:account-id:resource-type/resource-id
arn:partition:service:region:account-id:resource-type:resource-id
```

4장 데모에 쓸 대조군 — 전부 공식 문서의 예시다.

| 리소스 | ARN | 비는 칸 |
| --- | --- | --- |
| IAM user | `arn:aws:iam::123456789012:user/john` | 리전 |
| S3 객체 | `arn:aws:s3:::amzn-s3-demo-bucket/*` | 리전 · 계정 |
| SNS topic | `arn:aws:sns:us-east-1:123456789012:example-sns-topic-name` | 없음 |
| VPC | `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-0e9801d129EXAMPLE` | 없음 |

**비는 칸에 뜻이 있다.** IAM은 전역이라 리전이 없고, S3 버킷 이름은 파티션 전역에서 유일하니(V5)
계정까지 없다. 3장의 "글로벌인 것들"이 4장에서 ARN의 모양으로 다시 나타난다.

**⚠️ 두 공식 문서가 어긋난다 — 파티션 개수.**

| 페이지 | 나열한 파티션 |
| --- | --- |
| IAM ARN 레퍼런스 | `aws` · `aws-cn` · `aws-us-gov` (셋) |
| S3 버킷 이름 규칙 (V5) | `aws` · `aws-cn` · `aws-us-gov` · `aws-eusc` (넷) |

S3 쪽이 European Sovereign Cloud를 포함해 더 최신으로 보이지만, **어느 쪽이 옳은지 이 검증으로는
확정하지 못했다.** 따라서 본문에 **파티션 개수를 숫자로 쓰지 않는다.** "중국과 GovCloud는 별도
파티션"까지만 쓰면 두 페이지 모두와 어긋나지 않는다.

---

## V12 · VPC 구성 요소 중 무엇에 요금이 붙는가 — 부분 확인

계획서 1장(해체기)이 ENI·보안 그룹·키 페어·서브넷·라우팅 테이블·인터넷 게이트웨이 여섯을
"무료"라고 단정하려 했다. 근거를 찾은 것과 못 찾은 것이 갈린다.

출처: [What is Amazon VPC?](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)

> **There's no additional charge for using a VPC.** There are, however, charges for some VPC
> components, such as NAT gateways, IP Address Manager, traffic mirroring, Reachability Analyzer,
> and Network Access Analyzer.

> **Private IPv4 addresses (RFC 1918) are not charged.**

**확인된 것**: VPC 사용 자체에 추가 요금이 없다. 사설 IPv4는 과금되지 않는다. 요금이 붙는 것으로
공식 문서가 **이름을 든** 것은 NAT 게이트웨이·IPAM·트래픽 미러링·Reachability Analyzer·
Network Access Analyzer 다섯이다.

**확인되지 않은 것**: 위 문장은 `such as`로 열거하므로 **닫힌 목록이 아니다.** "목록에 없으니
무료"는 부재로부터의 추론이지 인용이 아니다. ENI와 키 페어는 이 문서가 아예 언급하지 않는다.

**따라서 1장에서는 여섯을 "무료"라고 쓰지 않는다.** 해체기의 요금 축은 근거가 있는 셋
(EC2는 켜 둔 시간, EBS는 보존되는 동안, 탄력적 IP는 쥐고 있는 동안)만 값을 채우고,
나머지 여섯은 **"12장에서 확인"으로 넘긴다.** 12장이 위 인용 두 줄을 근거로 답한다.

넘기는 것이 손해가 아니다. 1장에서 아홉 개 중 여섯이 답을 미루면 12장까지 끌고 갈 것이 남는다.

## V13 · 계정은 격리 단위이자 청구 단위이고, 둘은 뗄 수 있다 — 확인됨

2장이 "계정을 조직으로 묶으면 격리는 그대로 두고 청구만 합친다"고 쓰려 해서 확인했다.

출처: [What is AWS Organizations?](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)

> **AWS accounts are natural boundaries for permission, security, costs, and workloads.**

한 문장이 "계정은 격리 단위이자 청구 단위"를 통째로 받쳐 준다. 권한·보안·비용·워크로드 넷이 같은 경계에 걸려 있다.

> Organizations helps you centrally manage and govern your environment as you grow and scale your
> AWS resources ... and **simplify billing by using a single payment method for all of your accounts.**

> **Organizations provides you with a single consolidated bill.**

**2장에 쓸 것**: 격리와 청구가 같은 단위에 걸려 있으면서도 **청구만 따로 뗄 수 있다**. 조직으로 묶어도 계정 사이의 격리는 그대로다 — 위 첫 인용이 계정을 여전히 경계라고 부르고, 합쳐지는 것은 청구서 한 장뿐이다.

`iam_tutorial.html`이 다루는 SCP·OU는 이 문서의 범위 밖이다. **이름도 꺼내지 않는다.**

## V14 · 계정을 넘으려면 양쪽이 다 허락해야 한다 — 확인됨

2장이 "계정이 다르면 보내는 쪽과 받는 쪽이 둘 다 좋다고 해야 문이 열린다"고 써서 확인했다.

출처: [Cross-account policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html)

> When you make a cross-account request, AWS performs two evaluations. AWS evaluates the request
> in the trusting account and the trusted account. ... **The request is allowed only if both
> evaluations return a decision of `Allow`.**

> For cross-account requests, the requester in the trusted `AccountA` must have an identity-based
> policy. That policy must allow them to make a request to the resource in the trusting `AccountB`.
> **Additionally**, the resource-based policy in `AccountB` must allow the requester in `AccountA`
> to access the resource.

문서가 붙인 이름까지 있다 — 주체가 있는 쪽이 **trusted**, 리소스가 있는 쪽이 **trusting**이다.

**2장에 쓸 것**: "양쪽이 다 허락해야 한다"까지. **정책의 종류(아이덴티티 기반 / 리소스 기반)와 이름은 꺼내지 않는다** — 그건 `iam_tutorial.html`의 본론이고, 이 문서의 독자는 아직 IAM을 모른다. 2장은 "문이 두 개고 둘 다 열려야 한다"는 모양까지만 보이고 넘긴다.

## V15 · 리전 격리와 "글로벌인 것들"의 명단 — 확인됨

3장이 "리전은 서로 격리된 별개의 세계"와 "IAM·CloudFront·Route 53은 리전을 고르지 않는다"를
쓰려 해서 확인했다. 둘 다 한 페이지에 있다.

출처: [AWS service endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html)

**리전 격리** — 3장의 첫 기둥을 그대로 받친다.

> **If a service supports Regions, the resources in each Region are independent of similar
> resources in other Regions.** For example, you can create an Amazon EC2 instance or an Amazon
> SQS queue in one Region. When you do, the instance or queue is independent of instances or
> queues in all other Regions.

**글로벌 엔드포인트 명단** — 짐작이 아니라 열거된 목록이다.

> The following services each have a global endpoint that spans AWS Regions:
> AWS Cloud WAN · **Amazon CloudFront** · AWS Global Accelerator ·
> **AWS Identity and Access Management (IAM)** · AWS Organizations · **Amazon Route 53** ·
> AWS Shield Advanced · AWS WAF Classic

**3장에 쓸 것**: CloudFront·IAM·Route 53 셋으로 충분하다. 나머지 다섯은 이 문서의 독자가
아직 모르는 서비스이니 꺼내지 않는다.

**주의 — S3는 이 목록에 없다.** S3 버킷은 리전에 만든다. 리전을 넘는 것은 **이름의 유일성**뿐이고,
그건 다른 이야기다(V5). 3장이 S3를 "글로벌인 것들"에 같이 묶으면 틀린다 — 이름만 넘는다고
정확히 갈라 써야 하고, 범위가 어디까지인지는 8장으로 넘긴다.

## V16 · AZ는 서로의 장애로부터 격리되도록 설계돼 있다 — 확인됨. **다만 원인을 지정하지 않는다**

3장이 "한 건물이 **정전으로** 흔들려도 다른 건물까지 같이 흔들리지는 않는다"고 썼다. 뜻은 맞지만
**정전이라는 원인은 공식 문서가 말하지 않은 것**이다. 문서가 쓰는 표현은 원인을 특정하지 않는다.

출처 ①: [What is Amazon RDS?](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)

> Each AWS Region contains multiple distinct locations called Availability Zones, or AZs.
> **Each Availability Zone is engineered to be isolated from failures in other Availability Zones.**
> Each is engineered to provide inexpensive, low-latency network connectivity to other Availability
> Zones in the same AWS Region.

출처 ②: [Regions and Zones](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html)

> Although rare, failures can occur that affect the availability of instances that are in the same
> location. If you host all of your instances in a single location that is affected by a failure,
> none of your instances would be available.

> By launching EC2 instances in multiple Availability Zones, you can protect your applications
> from the failure of a single location in the Region.

**쓸 수 있는 것**: "AZ는 다른 AZ의 장애로부터 격리되도록 설계돼 있다", "한 곳이 무너져도 다른
곳의 인스턴스는 살아 있다", "그래서 AZ를 나눠 두면 한 위치의 장애를 견딘다".

**쓰면 안 되는 것**: 장애의 **원인을 지정하는 것**. 정전·화재·냉각 실패 같은 예시는 문서에 없다.
`failures`라고만 적혀 있고, 그 이상은 지어낸 것이 된다. 그리고 문서 자신이 `Although rare`와
`engineered to be`라고 쓴다 — **보장이 아니라 설계 목표**다. 3장도 그 온도를 지켜야 한다.

## V17 · 인스턴스 타입을 바꾸려면 먼저 중지해야 한다 — 확인됨

계획서 5장 데모의 `resize` 항목이 "먼저 중지해야 하므로 중지의 결과가 그대로 따라온다"는
인과 사슬을 썼는데 근거가 없었다. 5장 구현자가 직접 확인해 인용을 가져왔다.

출처: [Change the instance type of an EBS-backed instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/change-instance-type-of-ebs-backed-instance.html)

> **You must stop your instance before you can change its instance type.**

**따라서 쓸 수 있다**: 타입 변경은 중지를 거치므로 **중지의 결과가 그대로 따라온다** — 인스턴스
스토어는 사라지고(V8이 따로 못 박기도 한다), 퍼블릭 IPv4는 해제됐다가 새로 받는다(V1).

V8의 표가 타입 변경 행을 따로 두고 "The data does not persist"라고 적은 것과, 여기서 확인된
"중지를 거친다"가 같은 결론에 이른다. **두 경로가 일치하므로 5장은 인과를 써도 된다.**

## V18 · EBS 볼륨은 같은 AZ 안에서만 붙고, 스냅샷은 증분이며 S3에 있다 — 확인됨

계획서 6장이 근거 없이 쓰려던 셋을 6장 구현자가 직접 확인해 인용을 가져왔다.

출처 ①: Amazon EBS 사용자 안내서 — 볼륨 연결

> You can attach an available EBS volume to one or more of your instances that is in the
> **same Availability Zone** as the volume.

> You can attach volumes to instances that are in the **same Availability Zone only**.

출처 ②: [Amazon EBS snapshots](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html)

> A snapshot is an **incremental** backup, which means that we save only the blocks on the volume
> that have changed since the most recent snapshot.

> Snapshots are **stored in Amazon S3**, in S3 buckets that **you can't access directly**.

**6장에 쓸 것**: 볼륨이 AZ에 갇힌다는 것은 3장(서브넷은 AZ에 갇힌다)과 7장(ENI도 그렇다)이
같은 제약 위에 서 있다는 뜻이다. **AZ 하나가 세 리소스를 동시에 묶는다.**

**주의**: 스냅샷이 S3에 있다고 해서 8장에서 다룰 **내 버킷**에 보이는 것은 아니다. 원문이
`you can't access directly`라고 못 박는다. 8장이 버킷을 다룰 때 이 둘을 섞지 않아야 한다.

## V19 · ENI의 부착·이동과 탄력적 IP의 소유 — 확인됨

7장 구현자가 계획서의 근거 없는 주장들을 직접 확인해 인용을 가져왔다.

**기본 ENI는 뗄 수 없다.**
> Each instance has a default network interface, called the **primary network interface**.
> **You can't detach a primary network interface from an instance.**

**떼었다 붙이면 속성이 따라간다.**
> The attributes of a network interface **follow it** as it's attached or detached from an instance
> and reattached to another instance.

**ENI도 같은 AZ 안에서만 붙는다** — V18(볼륨)과 같은 제약이다.
> You can create and configure network interfaces and attach them to instances that you launch
> **in the same Availability Zone**.

**자동 할당 퍼블릭 IPv4는 기본 인터페이스에만 붙는다.**
> When you launch an instance, the IP address is assigned to the **primary** network interface.

**탄력적 IP는 계정 소유다** — V1의 "퍼블릭 IP는 계정 것이 아니다"와 정확히 대비된다.
> An Elastic IP address is **allocated to your AWS account, and is yours until you release it.**

> When you associate an Elastic IP address with an instance, it is also associated with the
> instance's primary network interface.

**7·12장에 쓸 것**: 이 대비가 EIP의 존재 이유를 설명한다. 자동 퍼블릭 IP는 빌려 온 것이라
놓으면 남에게 가고, EIP는 **놓아주기 전까지 내 것**이다. 12장의 "몇 개나 갖고 있나"(V2)가
바로 이 소유 때문에 성립한다.

**아직 안 쓴 확인 사실**: 보조 사설 IP는 인스턴스 사이에서 개별 재할당이 가능하다. 7장의 네
항목에 안 맞아 쓰지 않았다. 나중에 필요하면 이 줄을 근거로 쓴다.

**AZ 제약이 이제 셋을 묶는다** — 서브넷(V6·3장) · 볼륨(V18·6장) · ENI(여기·7장). 9장이
로드밸런서가 서브넷 둘을 요구하는 이유를 이 셋 위에 세운다.

## V20 · ENI도 인스턴스와 따로 죽는다 — 확인됨

1장 해체기가 ENI를 "인스턴스와 따로 살고 따로 죽는다"고 예고했는데, "따로 죽는다" 쪽의 근거가
없었다. 7장 구현자가 확인해 왔다.

출처: Elastic network interfaces — Termination behavior

> **Termination behavior** — You can set the termination behavior for a network interface that's
> attached to an instance. You can **specify whether the network interface should be automatically
> deleted** when you terminate the instance to which it's attached.

**주의 — 이 항목은 7장 리뷰에서 절차 위반으로 잡혔다.** 구현자가 확인은 했지만 근거를 코드
주석에만 남기고 이 파일에 등재하지 않아, 리뷰어가 "근거 파일에 없는 주장"으로 Important를
매겼다. **내용은 맞고 절차만 빠졌다.** 컨트롤러가 여기 등재해 닫는다.

**규칙 재확인**: 확인한 사실은 **반드시 이 파일에 등재한다.** 코드 주석은 보조이지 근거가 아니다.
검증 게이트는 "구현자가 WebFetch를 했는가"가 아니라 **"이 파일에 있는가"**다.

## V21 · S3의 성질 넷과 EBS의 다중 연결 — 확인됨

8장 구현자가 계획서의 근거 없는 주장들을 직접 확인해 인용을 가져왔다.

**객체는 통째로다.** 8장 퀴즈의 정답이 이 인용 위에 선다.
> Amazon S3 **never adds partial objects**; if you receive a success response, Amazon S3 added the
> **entire object** to the bucket. You cannot use `PutObject` to only update a single piece of
> metadata for an existing object. **You must put the entire object** with updated metadata if you
> want to update some values.

**디렉터리가 없다.**
> Amazon S3 general purpose buckets have a **flat structure** instead of a hierarchy like you would
> see in a file system.

**마운트가 아니라 HTTP다.**
> The REST API is an **HTTP interface** to Amazon S3. With the REST API, you use standard HTTP
> requests to create, fetch, and delete buckets and objects.

**동시 접근 시 부분 데이터는 없다.**
> if you make a PUT request to an existing key from one thread and perform a GET request on the
> same key from a second thread concurrently, you will get either the old data or the new data,
> but **never partial or corrupt data**.

**EBS의 다중 연결 — 예외가 있다.** V18의 "같은 AZ에만"에 조건이 하나 더 붙는다.
> **Multi-Attach enabled** volumes can be attached to **up to 16 instances**.

→ "EBS는 한 대에만 붙는다"고 **단정하면 틀린다.** 기본 동작과 Multi-Attach를 갈라 써야 한다.

**지운 버킷 이름은 남이 가져갈 수 있다** — V5의 경고를 8장이 실제로 썼다.
> After you delete a general purpose bucket in the shared global namespace, be aware that
> **another AWS account in the same partition can use the same** general purpose bucket name for a
> new bucket and can therefore potentially **receive requests intended for the deleted** bucket.

## V22 · S3는 리전 안 여러 AZ에 걸쳐 중복 저장된다 — 확인됨

8장 데모의 `az` 항목이 "S3는 AZ에 갇히지 않는다"의 근거로 쓴 것이다.

> you can **redundantly store objects across multiple Availability Zones**.

**8장에 쓸 것**: EBS는 AZ 하나에 갇히고(V18) S3는 여러 AZ에 걸친다. 이 대비가 6·7장이 세운
"AZ에 박힌 못 셋"(서브넷·볼륨·ENI)과 S3를 가르는 자리다.

**주의 — 이 항목도 V20과 똑같은 절차 위반으로 잡혔다.** 구현자가 확인은 했는데 근거를 코드
주석과 보고서에만 남기고 이 파일에 등재하지 않았다. **같은 위반이 두 번째다.**

**규칙을 다시 한번**: 확인한 사실은 **반드시 이 파일에 등재한다.** 검증 게이트는 "구현자가
WebFetch를 했는가"가 아니라 **"이 파일에 있는가"**다. 이후 모든 태스크의 dispatch에
"확인했으면 인용 전문을 보고서의 지정된 절에 적고, 컨트롤러가 등재할 수 있게 하라"를 명시한다.

## V23 · 입구 넷이 하는 일 — 확인됨

9장 구현자가 계획서의 근거 없는 주장 넷을 직접 확인해 인용을 가져왔다.

**IGW는 퍼블릭 주소를 가진 것만 지나간다. 그리고 라우팅 테이블의 타깃이다.**
> An internet gateway enables resources in your public subnets (such as EC2 instances) to connect
> to the internet **if the resource has a public IPv4 address or an IPv6 address.**

> An internet gateway provides a **target in your VPC route tables** for internet-routable traffic.

**NAT Gateway는 단방향이다.**
> You can use a NAT gateway so that instances in a private subnet can connect to services outside
> your VPC but **external services can't initiate a connection with those instances.**

> Instances in private subnets can connect to the internet through a public NAT gateway, but the
> instances **can't receive unsolicited inbound connections** from the internet.

**ALB는 7계층, NLB는 4계층이다.** 이 한 줄이 "무엇을 보느냐"라는 첫 갈림길의 근거다.
> An Application Load Balancer functions at the **application layer, the seventh layer** of the OSI
> model. … You can configure listener rules to route requests to different target groups **based on
> the content of the application traffic.**

> Support for **Path conditions.** You can configure rules for your listener that forward requests
> based on the URL in the request.

> A Network Load Balancer functions at the **fourth layer** of the OSI model.

**로드밸런서를 앞에 세우면 타깃에 퍼블릭 IP가 필요 없다.**
> Both internet-facing and internal load balancers route requests to your targets **using private
> IP addresses.** Therefore, your targets **do not need public IP addresses** to receive requests
> from an internal or an internet-facing load balancer.

**9·12장에 쓸 것**: 마지막 인용이 12장과 이어진다. 퍼블릭 IPv4는 개수만큼 시간당 과금되므로(V2),
로드밸런서를 앞에 세우는 것은 구조만이 아니라 **요금의 문제이기도 하다.**

## V24 · ALB 리스너 규칙의 조건 타입 — 확인됨

9장이 "ALB는 경로도 호스트 헤더도 본다"고 썼는데 V23은 `path-pattern`만 인용했다. 리뷰가
"호스트 헤더는 근거 파일에 없다"고 잡아 컨트롤러가 확인했다.

출처: [Listener rules for your Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-rules.html)

> Each rule other than the default rule can optionally include one of the following conditions:
> **`host-header`, `http-request-method`, `path-pattern`, and `source-ip`.** It can also optionally
> include one or both of the following conditions: `http-header` and `query-string`.

**호스트 헤더는 실제로 지원되는 조건 타입이다. 9장의 서술은 맞다.**

**함께 확인된 것 — 규칙 평가는 우선순위 순이다.**
> Rules are evaluated in **priority order, from the lowest value to the highest value.** The
> default rule is evaluated last.

이 문서는 규칙 평가 순서를 다루지 않는다(그건 통제에 가깝고 `aws_network_security.html`의 결이다).
**쓰지 않는다.**

**이 항목은 앞의 둘과 성격이 다르다.** V20·V22는 구현자가 확인하고 등재만 빠뜨린 것이고, 이것은
**확인 없이 쓴 것**이다. 결과적으로 맞았지만 절차로는 더 나쁘다.

## 검증 요약

| # | 대상 | 결과 |
|---|---|---|
| V1 | stop→start 시 퍼블릭 IPv4 | 확인됨. 재부팅은 원문에 없으므로 V8로 대체 |
| V2 | 퍼블릭 IPv4 과금 | 확인됨. 2024-02-01, 시간당 $0.005, **붙어 있어도 같은 값** |
| V3 | `DeleteOnTermination` | **설계가 틀렸다.** 축이 셋이고 CLI는 데이터 볼륨도 지운다 |
| V4 | NAT Gateway 과금 | 확인됨. 시간당 + GB당 + 퍼블릭 IP까지 세 겹 |
| V5 | S3 버킷 이름 유일성 | 확인됨. 전 세계가 아니라 **파티션 안** |
| V6 | AZ 이름↔ID | 확인됨. 무작위 매핑. 실제 CLI 출력 확보 |
| V7 | ALB/NLB 최소 서브넷 | 확인됨. ALB 둘 / NLB 하나. 고정 IP도 갈린다 |
| V8 | 인스턴스 스토어 수명 | 확인됨. 전체 표 확보 |
| V9 | Lambda 한계 | 확인됨. **"15분이 최대"는 함수로 한정해야 한다** |
| V10 | RDS가 안 주는 것 | 확인됨. 호스트 접근 불가 원문 확보 |
| V11 | ARN 빈 칸 | 확인됨. **파티션 개수는 문서끼리 어긋나므로 쓰지 않는다** |
| V12 | VPC 구성 요소 과금 | 부분 확인. VPC 자체·사설 IPv4는 무과금. **ENI·키 페어는 근거 없음 — 1장에서 "무료"라고 쓰지 않고 12장으로 넘긴다** |
| V13 | 계정 = 격리 단위 = 청구 단위 | 확인됨. 조직으로 묶으면 **격리는 그대로 두고 청구만** 합쳐진다 |
| V14 | 계정 경계를 넘는 조건 | 확인됨. **양쪽 평가가 모두 Allow일 때만** 통과. 정책 종류·이름은 IAM 문서의 몫이라 쓰지 않는다 |
| V15 | 리전 격리 · 글로벌 서비스 명단 | 확인됨. 리전 간 리소스는 독립. 글로벌 엔드포인트 명단에 CloudFront·IAM·Route 53이 있고 **S3는 없다** |
| V16 | AZ의 장애 격리 | 확인됨. 단 **원인(정전·화재)은 문서에 없다.** `failures`까지만, 그리고 `engineered to be`이지 보장이 아니다 |
| V17 | 타입 변경은 중지를 거치는가 | 확인됨. "You must stop your instance before you can change its instance type." 5장이 인과를 써도 된다 |
| V18 | EBS의 AZ 제약 · 스냅샷 | 확인됨. 볼륨은 **같은 AZ에만** 붙는다. 스냅샷은 증분이고 S3에 있지만 **직접 접근할 수 없다** |
| V19 | ENI 부착·이동 · EIP 소유 | 확인됨. 기본 ENI는 못 뗀다, 속성은 ENI를 따라간다, 같은 AZ에서만 붙는다, **EIP는 놓아주기 전까지 내 것** |
| V20 | ENI의 종료 동작 | 확인됨. 인스턴스 종료 시 함께 지울지 지정할 수 있다. **7장 리뷰에서 절차 위반(코드 주석에만 근거)으로 잡혀 여기 등재** |
| V21 | S3의 성질 넷 · EBS 다중 연결 | 확인됨. 객체는 통째로 / 평면 구조 / HTTP REST / 부분 데이터 없음. **Multi-Attach는 최대 16대 — "한 대에만"으로 단정하면 틀린다** |
| V22 | S3의 AZ 중복 저장 | 확인됨. `redundantly store objects across multiple Availability Zones`. **V20과 같은 절차 위반(주석에만 근거)으로 두 번째로 잡혀 여기 등재** |
| V23 | 입구 넷이 하는 일 | 확인됨. IGW는 퍼블릭 주소를 가진 것만·라우팅 타깃 / NAT GW 단방향 / **ALB 7계층·NLB 4계층** / LB 뒤 타깃은 퍼블릭 IP 불필요 |
| V24 | ALB 규칙 조건 타입 | 확인됨. `host-header` `path-pattern` `http-request-method` `source-ip`. **확인 없이 쓴 것이 결과적으로 맞았던 경우 — 절차로는 V20·V22보다 나쁘다** |

## 설계 문서에 반영할 것

1. **6장** — "루트와 추가 볼륨이 갈린다"를 "볼륨 종류 · 붙인 시점 · 콘솔이냐 CLI냐, 축이 셋"으로
   고친다. 그리고 최종 결정권이 AMI에 있다는 한 줄을 넣는다.
2. **11장** — "Lambda는 15분"을 "Lambda 함수의 타임아웃은 900초"로 좁힌다.
3. **4장** — 파티션 개수를 숫자로 쓰지 않는다.
4. **12장** — "안 쓰는 EIP에 돈이 나간다"를 "갖고 있는 퍼블릭 IPv4 개수만큼 나간다"로 고친다.
   쓰는 것과 노는 것의 값이 같으므로, 옛 상식대로 쓰면 그 자체가 오해를 남긴다.
