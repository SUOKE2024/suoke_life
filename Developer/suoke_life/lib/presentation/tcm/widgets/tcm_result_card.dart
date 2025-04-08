import 'package:flutter/material.dart';
import 'package:suoke_life/core/constants/app_colors.dart';
import 'package:suoke_life/domain/entities/tcm/tcm_diagnosis_result.dart';

class TcmResultCard extends StatelessWidget {
  final TcmDiagnosisResult diagnosis;

  const TcmResultCard({
    Key? key,
    required this.diagnosis,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFF5F5F5),
            Color(0xFFE8F5EF),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(15),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildMainResult(),
                const SizedBox(height: 16),
                _buildConstitutionSection(),
                const SizedBox(height: 16),
                _buildDiagnosisDetails(),
                const SizedBox(height: 16),
                _buildRecommendationsSection(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
      decoration: BoxDecoration(
        color: AppColors.SUOKE_GREEN,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(16),
          topRight: Radius.circular(16),
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.medical_services_outlined,
            color: Colors.white,
          ),
          const SizedBox(width: 8),
          const Text(
            '中医诊断结果',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const Spacer(),
          Text(
            diagnosis.timestamp,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMainResult() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '综合辨证结果',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.withAlpha(40)),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.SUOKE_GREEN.withAlpha(20),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.healing,
                  color: AppColors.SUOKE_GREEN,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      diagnosis.mainSyndrome,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    if (diagnosis.description != null && diagnosis.description!.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 4.0),
                        child: Text(
                          diagnosis.description!,
                          style: TextStyle(
                            color: Colors.grey.shade700,
                            fontSize: 14,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildConstitutionSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '体质辨识',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.withAlpha(40)),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppColors.SUOKE_ORANGE.withAlpha(20),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.person_outline,
                      color: AppColors.SUOKE_ORANGE,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      diagnosis.constitution,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                ],
              ),
              if (diagnosis.constitutionDescription != null && 
                  diagnosis.constitutionDescription!.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 8.0, left: 32.0),
                  child: Text(
                    diagnosis.constitutionDescription!,
                    style: TextStyle(
                      color: Colors.grey.shade700,
                      fontSize: 14,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDiagnosisDetails() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '四诊分析',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.withAlpha(40)),
          ),
          child: Column(
            children: [
              if (diagnosis.tongueDetails != null)
                _buildDetailItem(
                  icon: Icons.spa,
                  title: '舌诊',
                  value: diagnosis.tongueDetails!,
                ),
              if (diagnosis.tongueDetails != null)
                const Divider(),
              if (diagnosis.faceDetails != null)
                _buildDetailItem(
                  icon: Icons.face,
                  title: '面诊',
                  value: diagnosis.faceDetails!,
                ),
              if (diagnosis.faceDetails != null && diagnosis.pulseDetails != null)
                const Divider(),
              if (diagnosis.pulseDetails != null)
                _buildDetailItem(
                  icon: Icons.favorite,
                  title: '脉诊',
                  value: diagnosis.pulseDetails!,
                ),
              if (diagnosis.pulseDetails != null && diagnosis.audioDetails != null)
                const Divider(),
              if (diagnosis.audioDetails != null)
                _buildDetailItem(
                  icon: Icons.mic,
                  title: '声音分析',
                  value: diagnosis.audioDetails!,
                ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDetailItem({
    required IconData icon,
    required String title,
    required String value,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            size: 18,
            color: AppColors.SUOKE_GREEN,
          ),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '调理建议',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 8),
        if (diagnosis.herbs.isNotEmpty || diagnosis.formulas.isNotEmpty) ...[
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey.withAlpha(40)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (diagnosis.herbs.isNotEmpty) ...[
                  const Text(
                    '推荐草药',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: diagnosis.herbs.map((herb) {
                      return Chip(
                        label: Text(herb),
                        backgroundColor: AppColors.SUOKE_GREEN.withAlpha(40),
                        visualDensity: VisualDensity.compact,
                      );
                    }).toList(),
                  ),
                ],
                if (diagnosis.herbs.isNotEmpty && diagnosis.formulas.isNotEmpty)
                  const SizedBox(height: 12),
                if (diagnosis.formulas.isNotEmpty) ...[
                  const Text(
                    '推荐方剂',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: diagnosis.formulas.map((formula) {
                      return Chip(
                        label: Text(formula),
                        backgroundColor: AppColors.SUOKE_ORANGE.withAlpha(40),
                        visualDensity: VisualDensity.compact,
                      );
                    }).toList(),
                  ),
                ],
              ],
            ),
          ),
        ],
        if (diagnosis.lifestyle != null && diagnosis.lifestyle!.isNotEmpty) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey.withAlpha(40)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '生活方式建议',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  diagnosis.lifestyle!,
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
          ),
        ],
        if (diagnosis.diet != null && diagnosis.diet!.isNotEmpty) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey.withAlpha(40)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '饮食建议',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  diagnosis.diet!,
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}